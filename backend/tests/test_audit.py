import os
import sqlite3

from app.audit.store import AuditStore


def test_audit_store_logging_and_verification():
    test_db = "test_audit.db"
    if os.path.exists(test_db):
        os.remove(test_db)
        
    store = AuditStore(db_path=test_db)
    
    payload1 = {"steps": []}
    store.log_decision(payload1, "ALLOW", "Safe.")
    
    payload2 = {"steps": [{"tool_name": "malicious"}]}
    store.log_decision(payload2, "BLOCK", "Blocked.")
    
    logs = store.get_logs()
    assert len(logs) == 2
    
    verify_result = store.verify_chain()
    assert verify_result["valid"] is True
    
    # Tamper with the database
    with sqlite3.connect(test_db) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE audit_logs SET decision = 'ALLOW' WHERE decision = 'BLOCK'")
        conn.commit()
        
    verify_result_after_tamper = store.verify_chain()
    assert verify_result_after_tamper["valid"] is False
    assert verify_result_after_tamper["broken_at_id"] is not None
    
    if os.path.exists(test_db):
        try:
            os.remove(test_db)
        except PermissionError:
            pass # Windows sqlite3 lock bug
