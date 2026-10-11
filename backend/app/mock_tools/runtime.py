from typing import Any, Dict


class MockToolRuntime:
    def __init__(self):
        pass

    def execute(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        print(f"[MOCK RUNTIME] Dispatching {tool_name} with args {args}")
        
        if tool_name == "database_query":
            return {"status": "success", "rows": [{"id": 1, "data": "mocked row"}]}
            
        elif tool_name == "file_read":
            return {"content": "mock file content for " + str(args.get("path", ""))}
            
        elif tool_name == "file_write":
            return {"status": "written", "bytes": len(str(args.get("content", "")))}
            
        elif tool_name == "http_post":
            return {"status": 200, "body": "ok from mock server"}
            
        elif tool_name == "email_send":
            return {"status": "queued", "recipient": args.get("to", "unknown")}
            
        elif tool_name == "shell_exec":
            return {"stdout": "mock output from shell", "code": 0}
            
        else:
            return {"error": "Unknown tool"}
