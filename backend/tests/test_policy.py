from app.policy.decision import evaluate_policy
from app.schemas import RuleResult, InspectorResult

def test_policy_allow():
    res = evaluate_policy(0.1, [], [])
    assert res["decision"] == "ALLOW"
    assert res["rationale"] == "Safe."

def test_policy_block_ml_score():
    res = evaluate_policy(0.95, [], [])
    assert res["decision"] == "BLOCK"
    assert "exceeds TAU_BLOCK" in res["rationale"]

def test_policy_block_critical_rule():
    rule = RuleResult(rule_id="R1", rule_name="Mock", triggered=True, severity="Critical")
    res = evaluate_policy(0.1, [rule], [])
    assert res["decision"] == "BLOCK"

def test_policy_confirm_high_score():
    res = evaluate_policy(0.80, [], [])
    assert res["decision"] == "CONFIRM"

def test_policy_revise_high_rules():
    rule = RuleResult(rule_id="R2", rule_name="Mock2", triggered=True, severity="High")
    res = evaluate_policy(0.1, [rule], [])
    assert res["decision"] == "REVISE"

def test_policy_confirm_multiple_high_rules():
    rule1 = RuleResult(rule_id="R2", rule_name="Mock2", triggered=True, severity="High")
    rule2 = RuleResult(rule_id="R3", rule_name="Mock3", triggered=True, severity="High")
    res = evaluate_policy(0.1, [rule1, rule2], [])
    assert res["decision"] == "CONFIRM"
