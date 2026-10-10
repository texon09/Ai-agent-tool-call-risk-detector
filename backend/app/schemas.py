from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class MCPMeta(BaseModel):
    server_name: Optional[str] = None
    tool_schema: Optional[Dict[str, Any]] = None
    resource_uris: Optional[List[str]] = None

class AnalyzeRequest(BaseModel):
    plan: dict = Field(..., description="The planned sequence of tool calls")
    context: Optional[dict] = None
    mcp_meta: Optional[MCPMeta] = None

class AnalyzeResponse(BaseModel):
    action: str = Field(..., pattern="^(ALLOW|CONFIRM|REVISE|BLOCK)$")
    risk_score: float
    critical_violations: int
    rule_hits: List[str]
    rationale: str
    feature_contributions: Dict[str, float]
    model_votes: Dict[str, Any]
    latency_ms: float
    audit_id: str

class RuleResult(BaseModel):
    rule_id: str
    rule_name: str
    triggered: bool
    severity: str
    reason: Optional[str] = None
    step_id: Optional[str] = None

class InspectorResult(BaseModel):
    scanner_name: str
    triggered: bool
    severity: str
    reason: Optional[str] = None
    match_preview: Optional[str] = None

class MetricSummary(BaseModel):
    total_requests: int
    blocked_requests: int
    feature_importance: Dict[str, float]
