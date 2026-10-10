from typing import List, Dict, Any
from app.schemas import RuleResult, InspectorResult

# Thresholds
TAU_BLOCK = 0.90
TAU_CONFIRM = 0.75
TAU_HIGH = 0.60
TAU_MEDIUM = 0.40

def evaluate_policy(ml_score: float, rule_results: List[RuleResult], inspector_results: List[InspectorResult]) -> Dict[str, Any]:
    all_violations = rule_results + inspector_results
    critical_violations = sum(1 for r in all_violations if r.severity == 'Critical')
    high_violations = sum(1 for r in all_violations if r.severity == 'High')
    
    rationale_parts = []
    rule_hits = []
    
    if critical_violations > 0:
        rationale_parts.append(f"Blocked due to {critical_violations} critical violations.")
    if ml_score >= TAU_BLOCK:
        rationale_parts.append(f"ML score {ml_score:.2f} exceeds TAU_BLOCK ({TAU_BLOCK}).")
        
    for v in all_violations:
        if isinstance(v, RuleResult):
            hit_str = f"Rule {v.rule_id} ({v.rule_name}) triggered: {v.reason}"
            rationale_parts.append(hit_str)
            rule_hits.append(v.rule_id)
        else:
            hit_str = f"Scanner {v.scanner_name} triggered: {v.reason}"
            rationale_parts.append(hit_str)
            rule_hits.append(v.scanner_name)

    rationale = " | ".join(rationale_parts) if rationale_parts else "Safe."

    if critical_violations > 0 or ml_score >= TAU_BLOCK:
        action = "BLOCK"
    elif high_violations > 1 or ml_score >= TAU_CONFIRM:
        action = "CONFIRM"
    elif high_violations == 1 or ml_score >= TAU_HIGH:
        action = "REVISE"
    elif ml_score >= TAU_MEDIUM:
        action = "REVISE"
    else:
        action = "ALLOW"
        
    return {
        "action": action,
        "rationale": rationale,
        "critical_violations": critical_violations,
        "rule_hits": rule_hits
    }
