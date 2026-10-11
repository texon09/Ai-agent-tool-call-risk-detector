import time

from app.audit.store import AuditStore
from app.policy.decision import evaluate_policy
from app.rules.engine import RuleEngine
from app.rules.inspector import ArgumentInspector
from app.schemas import AnalyzeRequest, AnalyzeResponse
from fastapi import APIRouter

router = APIRouter()
rule_engine = RuleEngine()
inspector = ArgumentInspector()
audit_store = AuditStore(db_path="audit.db")


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_plan(request: AnalyzeRequest):
    start_time = time.perf_counter()
    try:
        # 1. Feature Extraction & 2. ML Score (Mocked / default 0.1)
        score = 0.1

        # 3. Rule Engine
        rule_results = rule_engine.evaluate(request.plan)

        # 4. Argument Inspector
        inspector_results = inspector.scan(request.plan)

        # 5. Policy Decision
        policy_result = evaluate_policy(score, rule_results, inspector_results)
        action = policy_result.get("action") or policy_result.get("decision", "BLOCK")
        rationale = policy_result["rationale"]

        # 6. Audit Logger
        payload = request.model_dump()
        audit_id = audit_store.log_decision(payload, action, rationale)

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        return AnalyzeResponse(
            action=action,
            decision=action,
            risk_score=score,
            score=score,
            critical_violations=policy_result.get("critical_violations", 0),
            rule_hits=policy_result.get("rule_hits", []),
            rationale=rationale,
            feature_contributions={},
            model_votes={},
            latency_ms=round(latency_ms, 2),
            audit_id=str(audit_id or ""),
        )
    except Exception as e:
        latency_ms = (time.perf_counter() - start_time) * 1000.0
        return AnalyzeResponse(
            action="BLOCK",
            decision="BLOCK",
            risk_score=1.0,
            score=1.0,
            critical_violations=1,
            rule_hits=["internal_error"],
            rationale=f"Internal Error: {str(e)}",
            feature_contributions={},
            model_votes={},
            latency_ms=round(latency_ms, 2),
            audit_id="",
        )
