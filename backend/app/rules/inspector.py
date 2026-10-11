import re
from typing import Any, Dict, List

from app.schemas import InspectorResult


class ArgumentInspector:
    SCANNERS = [
        {
            "name": "Credential patterns",
            "pattern": re.compile(r"(?i)(api_key|token|secret)[=:]\s*[\"']?[a-zA-Z0-9_-]{16,}[\"']?"),
            "severity": "Critical"
        },
        {
            "name": "Sensitive file paths",
            "pattern": re.compile(r"(/etc/passwd|\.aws/credentials|\.env)"),
            "severity": "High"
        },
        {
            "name": "Suspicious URLs",
            "pattern": re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),
            "severity": "High"
        },
        {
            "name": "SQL injection patterns",
            "pattern": re.compile(r"(?i)(UNION\s+SELECT|DROP\s+TABLE|--)"),
            "severity": "Critical"
        },
        {
            "name": "Path traversal",
            "pattern": re.compile(r"(\.\./|\.\.%2F)"),
            "severity": "High"
        },
        {
            "name": "Base64 blobs",
            "pattern": re.compile(r"^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$"),
            "severity": "Medium"
        },
        {
            "name": "PII patterns",
            "pattern": re.compile(r"\b(\d{3}-\d{2}-\d{4}|\d{4}-\d{4}-\d{4}-\d{4})\b"),
            "severity": "High"
        }
    ]

    def __init__(self):
        pass

    def scan(self, plan: Dict[str, Any]) -> List[InspectorResult]:
        results = []
        plan_str = str(plan)
        
        for scanner in self.SCANNERS:
            match = scanner["pattern"].search(plan_str)
            # Special check for base64 to avoid false positives on small words
            if scanner["name"] == "Base64 blobs" and match:
                if len(match.group(0)) < 100:
                    continue

            if match:
                results.append(InspectorResult(
                    scanner_name=scanner["name"],
                    triggered=True,
                    severity=scanner["severity"],
                    reason=f"Regex matched: {scanner['name']}",
                    match_preview=match.group(0)[:50]
                ))
        return results
