import hashlib
import json
import sqlite3
import threading
from contextlib import closing
from datetime import datetime
from typing import Any, Dict, List


class AuditStore:
    def __init__(self, db_path: str = "audit.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS audit_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        prev_hash TEXT NOT NULL,
                        current_hash TEXT NOT NULL,
                        payload TEXT NOT NULL,
                        decision TEXT NOT NULL,
                        rationale TEXT NOT NULL
                    )
                ''')

    def log_decision(self, payload: Dict[str, Any], decision: str, rationale: str) -> str:
        with self.lock:
            with closing(sqlite3.connect(self.db_path)) as conn:
                with conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT current_hash FROM audit_logs ORDER BY id DESC LIMIT 1")
                    row = cursor.fetchone()
                    prev_hash = row[0] if row else "GENESIS"

                    timestamp = datetime.utcnow().isoformat()
                    payload_str = json.dumps(payload, sort_keys=True)
                    
                    # SHA256(prev_hash + str(timestamp) + json.dumps(payload) + decision)
                    hash_input = f"{prev_hash}{timestamp}{payload_str}{decision}".encode('utf-8')
                    current_hash = hashlib.sha256(hash_input).hexdigest()

                    cursor.execute('''
                        INSERT INTO audit_logs (timestamp, prev_hash, current_hash, payload, decision, rationale)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (timestamp, prev_hash, current_hash, payload_str, decision, rationale))
                    return current_hash

    def verify_chain(self) -> Dict[str, Any]:
        with closing(sqlite3.connect(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, timestamp, prev_hash, current_hash, payload, decision FROM audit_logs ORDER BY id ASC")
            rows = cursor.fetchall()

        expected_prev = "GENESIS"
        for row in rows:
            r_id, timestamp, prev_hash, current_hash, payload, decision = row
            
            if prev_hash != expected_prev:
                return {"valid": False, "broken_at_id": r_id, "reason": "prev_hash mismatch"}
            
            hash_input = f"{prev_hash}{timestamp}{payload}{decision}".encode('utf-8')
            recalc_hash = hashlib.sha256(hash_input).hexdigest()
            
            if recalc_hash != current_hash:
                return {"valid": False, "broken_at_id": r_id, "reason": "current_hash mismatch"}
                
            expected_prev = current_hash
            
        return {"valid": True, "broken_at_id": None, "reason": "Chain intact"}

    def get_logs(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        with closing(sqlite3.connect(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT ? OFFSET ?", (limit, offset))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
