from typing import List, Dict, Any
from app.schemas import RuleResult

class RuleEngine:
    ALLOWED_TOOLS = ["database_query", "file_read", "file_write", "http_post", "email_send", "shell_exec"]

    def __init__(self):
        pass

    def evaluate(self, plan: Dict[str, Any]) -> List[RuleResult]:
        results = []
        steps = plan.get("steps", [])
        for i, step in enumerate(steps):
            tool_name = step.get("tool_name", "")
            args = step.get("arguments", {})
            step_id = str(i)

            # R1: Permission check
            if tool_name not in self.ALLOWED_TOOLS:
                results.append(RuleResult(
                    rule_id="R1", rule_name="Permission check", triggered=True,
                    severity="Critical", reason=f"Tool {tool_name} not allowed", step_id=step_id
                ))

            # R2: Irreversibility check
            if tool_name in ["database_query", "shell_exec"]:
                query = str(args).upper()
                if any(x in query for x in ["DROP", "DELETE", "UPDATE", "RM -RF"]):
                    results.append(RuleResult(
                        rule_id="R2", rule_name="Irreversibility check", triggered=True,
                        severity="High", reason="Irreversible action detected without backup", step_id=step_id
                    ))

            # R3: Sensitivity check
            if "passwd" in str(args) or ".aws" in str(args):
                results.append(RuleResult(
                    rule_id="R3", rule_name="Sensitivity check", triggered=True,
                    severity="High", reason="Access to sensitive resource tags", step_id=step_id
                ))

            # R4: Egress check
            if tool_name == "http_post":
                url = args.get("url", "")
                if url and "internal-network" not in url:
                    results.append(RuleResult(
                        rule_id="R4", rule_name="Egress check", triggered=True,
                        severity="Critical", reason="Data sent outside network boundaries", step_id=step_id
                    ))

            # R5: Budget check
            if tool_name == "database_query" and len(str(args.get("query", ""))) > 500:
                results.append(RuleResult(
                    rule_id="R5", rule_name="Budget check", triggered=True,
                    severity="Medium", reason="Resource usage might exceed quota", step_id=step_id
                ))
            
            # R6: Suspicious pattern check
            if tool_name == "shell_exec" and "nmap" in str(args):
                results.append(RuleResult(
                    rule_id="R6", rule_name="Suspicious pattern check", triggered=True,
                    severity="High", reason="Iterative probing detected", step_id=step_id
                ))

            # R7: Scope ambiguity check
            if "*" in str(args) or "%" in str(args):
                results.append(RuleResult(
                    rule_id="R7", rule_name="Scope ambiguity check", triggered=True,
                    severity="Medium", reason="Wildcard usage in queries/paths", step_id=step_id
                ))

            # R8: Broad-scope check
            if "limit" not in str(args).lower() and tool_name == "database_query":
                results.append(RuleResult(
                    rule_id="R8", rule_name="Broad-scope check", triggered=True,
                    severity="High", reason="Action might affect many records", step_id=step_id
                ))

            # R9: Untrusted-input check
            if tool_name == "shell_exec" and args.get("cmd", "").startswith("curl"):
                results.append(RuleResult(
                    rule_id="R9", rule_name="Untrusted-input check", triggered=True,
                    severity="Critical", reason="Direct execution of user input", step_id=step_id
                ))

        return results
