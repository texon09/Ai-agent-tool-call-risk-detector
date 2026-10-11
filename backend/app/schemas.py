from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MCPMeta(BaseModel):
    server_name: Optional[str] = None
    tool_schema: Optional[Dict[str, Any]] = None
    resource_uris: Optional[List[str]] = None


class AnalyzeRequest(BaseModel):
    plan: dict = Field(..., description="The planned sequence of tool calls")
    context: Optional[dict] = None
    mcp_meta: Optional[MCPMeta] = None


class ModelScores(BaseModel):
    model_config = {"protected_namespaces": ()}

    decision_tree: float
    random_forest: float
    xgboost: float
    isolation_forest: float
    ensemble: float


class AnalyzeResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    action: str = Field(..., pattern="^(ALLOW|CONFIRM|REVISE|BLOCK)$")
    risk_score: float
    critical_violations: int = 0
    rule_hits: List[str] = Field(default_factory=list)
    rationale: str
    feature_contributions: Dict[str, float] = Field(default_factory=dict)
    model_scores: ModelScores
    model_votes: Dict[str, Any] = Field(default_factory=dict)
    latency_ms: float = 0.0
    audit_id: str = ""
    decision: Optional[str] = None
    score: Optional[float] = None

    def model_post_init(self, __context: Any) -> None:
        if self.decision is None:
            self.decision = self.action
        if self.score is None:
            self.score = self.risk_score
        if not self.model_votes and self.model_scores:
            self.model_votes = {
                "rf_prob": self.model_scores.random_forest,
                "xgb_prob": self.model_scores.xgboost,
                "dt_prob": self.model_scores.decision_tree,
                "iso_flag": int(self.model_scores.isolation_forest >= 0.5),
            }


class RuleResult(BaseModel):
    rule_id: str
    rule_name: str
    triggered: bool
    severity: str
    reason: Optional[str] = None
    step_id: Optional[str] = None
    flag: Optional[str] = None
    step_triggered: Optional[int] = None


class InspectorResult(BaseModel):
    scanner_name: str
    triggered: bool
    severity: str
    reason: Optional[str] = None
    match_preview: Optional[str] = None
    evidence: Optional[str] = None
    step: Optional[int] = None


class ModelMetrics(BaseModel):
    model_config = {"protected_namespaces": ()}

    f1: float
    precision: float
    recall: float
    auroc: float
    latency_ms: float


class MetricsResponse(BaseModel):
    models: Dict[str, ModelMetrics]
    available: bool = True
    detail: Optional[str] = None


class Scenario(BaseModel):
    name: str
    description: str
    plan: Dict[str, Any]
    expected_decision: str = Field(..., pattern="^(ALLOW|CONFIRM|REVISE|BLOCK)$")


class ScenarioResponse(BaseModel):
    scenarios: List[Scenario]
