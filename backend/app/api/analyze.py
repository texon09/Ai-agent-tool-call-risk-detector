"""Endpoint for plan risk analysis, combining ML scoring, deterministic rules, and policy."""

from __future__ import annotations

import logging
import os
from pathlib import Path
import time
from typing import Any
import numpy as np
import pandas as pd

from fastapi import APIRouter

from app.audit.store import AuditStore
from app.features.extractor import FEATURE_NAMES, extract_features
from app.ml.ensemble import get_model_scores, model_votes, score_risk
from app.ml.loader import load_model
from app.policy.decision import decide
from app.rules.engine import RuleEngine
from app.rules.inspector import ArgumentInspector
from app.schemas import AnalyzeRequest, AnalyzeResponse, ModelScores

logger = logging.getLogger(__name__)
router = APIRouter()

rule_engine = RuleEngine()
inspector = ArgumentInspector()
audit_store = AuditStore(db_path=os.getenv("DATABASE_URL", "sqlite:///audit.db"))

REPO_ROOT = Path(__file__).resolve().parents[3]
MODEL_DIR = os.getenv("MODEL_DIR", str(REPO_ROOT / "artifacts" / "models" / "v2"))
DATA_DIR = os.getenv("DATA_DIR", str(REPO_ROOT / "data" / "processed"))

# Lazy cache for ML models
_model_cache: dict[str, Any] = {
    "loaded": False,
    "manifest": None,
    "models": None,
    "feature_importances": None,
}


def _get_ml_models():
    """Load and cache trained ML artifacts."""
    if _model_cache["loaded"]:
        return _model_cache["manifest"], _model_cache["models"]

    try:
        manifest, models = load_model(MODEL_DIR, DATA_DIR if os.path.exists(DATA_DIR) else None)
        _model_cache["manifest"] = manifest
        _model_cache["models"] = models
        _model_cache["loaded"] = True

        # Precompute feature importance map for contribution attribution
        if "random_forest" in models:
            rf = models["random_forest"]
            if hasattr(rf, "feature_importances_"):
                fi = rf.feature_importances_
                _model_cache["feature_importances"] = dict(zip(FEATURE_NAMES, fi, strict=False))

        logger.info("Successfully loaded ML models from %s", MODEL_DIR)
        return manifest, models
    except Exception as exc:
        logger.warning("ML model loading failed, falling back to rule-only mode: %s", exc)
        return None, None


def _calculate_feature_contributions(feat_vec: np.ndarray, top_k: int = 5) -> dict[str, float]:
    """Calculate the top feature contributions based on normalized feature weights."""
    importances = _model_cache.get("feature_importances") or {}
    contributions = {}
    for i, name in enumerate(FEATURE_NAMES):
        val = float(feat_vec[i])
        weight = importances.get(name, 0.02)
        score = abs(val) * weight
        if score > 0:
            contributions[name] = round(float(score), 4)

    # Sort descending and take top_k
    sorted_items = sorted(contributions.items(), key=lambda x: x[1], reverse=True)[:top_k]
    return dict(sorted_items)


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_plan(request: AnalyzeRequest) -> AnalyzeResponse:
    """Analyze an incoming tool call plan and evaluate risk."""
    start_time = time.perf_counter()

    try:
        mcp_meta_dict = request.mcp_meta.model_dump() if request.mcp_meta else None
        
        # 1. Feature Extraction
        feat_vec = extract_features(request.plan, mcp_meta=mcp_meta_dict)
        feat_df = pd.DataFrame([feat_vec], columns=FEATURE_NAMES)

        # 2. ML Risk Scoring
        manifest, models = _get_ml_models()
        votes: dict[str, Any] = {}
        ml_risk_score = 0.1  # default benign prior if models unavailable
        ind_scores = {
            "decision_tree": 0.0,
            "random_forest": 0.0,
            "xgboost": 0.0,
            "isolation_forest": 0.0,
        }

        if models and manifest:
            ind_scores = get_model_scores(feat_df, models, manifest)
            rf_prob = ind_scores["random_forest"]
            xgb_prob = ind_scores["xgboost"]
            dt_prob = ind_scores["decision_tree"]

            iso_thresh = float(manifest.get("anomaly_threshold", 0.0))
            iso_score = float(models["isolation_forest"].decision_function(feat_df)[0])
            iso_flag = int(iso_score < iso_thresh)

            weights_dict = manifest.get("ensemble_weights", {"rf": 0.40, "xgb": 0.40, "dt": 0.10, "iso": 0.10})
            calibrator = models["calibrator"]
            cal_method = manifest.get("calibration_method", "isotonic")

            iso_risk_val = ind_scores["isolation_forest"]
            calibrated_arr = score_risk(
                p_HR_rf=rf_prob,
                p_HR_xgb=xgb_prob,
                p_HR_dt=dt_prob,
                p_iso=iso_risk_val,
                weights=weights_dict,
                calibrator=calibrator,
                cal_method=cal_method,
            )
            ml_risk_score = float(np.clip(calibrated_arr[0], 0.0, 1.0))
            votes = model_votes(rf_prob, xgb_prob, dt_prob, iso_flag)

        model_scores_obj = ModelScores(
            decision_tree=round(float(ind_scores["decision_tree"]), 4),
            random_forest=round(float(ind_scores["random_forest"]), 4),
            xgboost=round(float(ind_scores["xgboost"]), 4),
            isolation_forest=round(float(ind_scores["isolation_forest"]), 4),
            ensemble=round(float(ml_risk_score), 4),
        )

        feat_contributions = _calculate_feature_contributions(feat_vec)

        # 3. Rule Engine Execution
        rule_results = rule_engine.evaluate(request.plan)

        # 4. Argument Inspector Scanning
        inspector_results = inspector.scan(request.plan)

        # 5. Policy Decision Layer
        policy_result = decide(
            risk_score=ml_risk_score,
            rule_results=rule_results,
            inspector_results=inspector_results,
        )

        action = policy_result["action"]
        rationale = policy_result["rationale"]
        critical_violations = policy_result.get("critical_violations", 0)
        rule_hits = policy_result.get("rule_hits", [])

        # 6. Audit Trail Logging
        payload = request.model_dump()
        trajectory_id = (
            request.context.get("trajectory_id")
            if request.context
            else payload.get("trajectory_id")
        )
        audit_id = audit_store.log_decision(
            payload=payload,
            decision=action,
            rationale=rationale,
            trajectory_id=trajectory_id,
        )

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        return AnalyzeResponse(
            action=action,
            decision=action,
            risk_score=round(ml_risk_score, 4),
            score=round(ml_risk_score, 4),
            critical_violations=critical_violations,
            rule_hits=rule_hits,
            rationale=rationale,
            feature_contributions=feat_contributions,
            model_scores=model_scores_obj,
            model_votes=votes,
            latency_ms=round(latency_ms, 2),
            audit_id=str(audit_id),
        )

    except Exception as exc:
        # Strict Fail-Closed Security Policy: any failure returns audited BLOCK
        logger.error("Analyze plan failed, enforcing fail-closed BLOCK: %s", exc, exc_info=True)
        latency_ms = (time.perf_counter() - start_time) * 1000.0
        rationale = f"Blocked: internal security evaluation failed closed ({type(exc).__name__}: {str(exc)})"
        
        try:
            audit_id = audit_store.log_decision(
                payload=request.model_dump() if "request" in locals() else {"error": str(exc)},
                decision="BLOCK",
                rationale=rationale,
            )
        except Exception:
            audit_id = "fail-closed-emergency"

        return AnalyzeResponse(
            action="BLOCK",
            decision="BLOCK",
            risk_score=1.0,
            score=1.0,
            critical_violations=1,
            rule_hits=["internal_error"],
            rationale=rationale,
            feature_contributions={},
            model_scores=ModelScores(
                decision_tree=1.0,
                random_forest=1.0,
                xgboost=1.0,
                isolation_forest=1.0,
                ensemble=1.0,
            ),
            model_votes={},
            latency_ms=round(latency_ms, 2),
            audit_id=str(audit_id),
        )
