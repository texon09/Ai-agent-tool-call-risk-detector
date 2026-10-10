from app.rules.inspector import ArgumentInspector

def test_credential_scanner():
    inspector = ArgumentInspector()
    
    plan_safe = {"steps": [{"tool_name": "database_query", "arguments": {"query": "SELECT * FROM users"}}]}
    plan_unsafe = {"steps": [{"tool_name": "file_write", "arguments": {"content": "API_KEY='AIzaSyA_abcdefghijklmnopqrstuvwx'"}}]}
    
    assert len(inspector.scan(plan_safe)) == 0
    
    results = inspector.scan(plan_unsafe)
    assert any(r.scanner_name == "Credential patterns" for r in results)

def test_sql_injection_scanner():
    inspector = ArgumentInspector()
    
    plan_unsafe = {"steps": [{"tool_name": "database_query", "arguments": {"query": "SELECT * FROM users UNION SELECT * FROM passwords"}}]}
    
    results = inspector.scan(plan_unsafe)
    assert any(r.scanner_name == "SQL injection patterns" for r in results)

def test_path_traversal():
    inspector = ArgumentInspector()
    plan_unsafe = {"steps": [{"tool_name": "file_read", "arguments": {"path": "../../../etc/passwd"}}]}
    results = inspector.scan(plan_unsafe)
    assert any(r.scanner_name == "Path traversal" for r in results)
    assert any(r.scanner_name == "Sensitive file paths" for r in results)
