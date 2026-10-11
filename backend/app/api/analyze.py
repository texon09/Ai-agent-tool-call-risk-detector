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
    try:
        # 1. Feature Extraction (Mocked)
        # 2. ML Score (Mocked)
        score = 0.1 
        
        # 3. Rule Engine
        rule_results = rule_engine.evaluate(request.plan)
        
        # 4. Argument Inspector
        inspector_results = inspector.scan(request.plan)
        
        # 5. Policy Decision
        policy_result = evaluate_policy(score, rule_results, inspector_results)
        decision = policy_result["decision"]
        rationale = policy_result["rationale"]
        
        # 6. Audit Logger
        payload = request.model_dump()
        audit_store.log_decision(payload, decision, rationale)
        
        return AnalyzeResponse(
            decision=decision,
            score=score,
            rationale=rationale
        )
    except Exception as e:
        return AnalyzeResponse(decision="BLOCK", score=1.0, rationale=f"Internal Error: {str(e)}")
