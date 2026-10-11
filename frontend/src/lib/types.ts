export interface ModelScores {
  decision_tree?: number;
  random_forest?: number;
  xgboost?: number;
  isolation_forest?: number;
  ensemble?: number;
}

export interface ModelVotes {
  rf_prob?: number;
  xgb_prob?: number;
  dt_prob?: number;
  iso_flag?: number | boolean;
}

export interface AnalyzeResponse {
  action: "ALLOW" | "CONFIRM" | "REVISE" | "BLOCK";
  decision?: string;
  risk_score: number;
  score?: number;
  critical_violations: number;
  rule_hits: string[];
  rationale: string;
  feature_contributions: Record<string, number>;
  model_scores?: ModelScores;
  model_votes?: ModelVotes;
  latency_ms: number;
  audit_id: string;
}

export interface Scenario {
  name: string;
  description: string;
  plan: Record<string, any>;
  expected_decision: "ALLOW" | "CONFIRM" | "REVISE" | "BLOCK";
}

export interface ModelMetrics {
  f1: number;
  precision: number;
  recall: number;
  auroc: number;
  latency_ms: number;
}

export interface MetricsResponse {
  available: boolean;
  models: Record<string, ModelMetrics>;
  detail?: string;
}

export interface AuditRecord {
  id: number;
  audit_id: string;
  trajectory_id: string;
  timestamp: string;
  prev_hash: string;
  current_hash: string;
  payload: string;
  decision: string;
  rationale: string;
}

export interface AuditVerifyResponse {
  valid: boolean;
  broken_at_id?: string | null;
  reason: string;
}
