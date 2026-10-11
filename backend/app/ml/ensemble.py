"""Ensemble scoring and calibration."""

import json
import os
from pathlib import Path
from typing import Any
import numpy as np
import pandas as pd

try:
    from app.ml.calibrate import apply_calibrator
except ImportError:
    from backend.app.ml.calibrate import apply_calibrator

DEFAULT_WEIGHTS = {
    "rf": 0.40,
    "xgb": 0.40,
    "dt": 0.10,
    "iso": 0.10,
}


def load_ensemble_weights(manifest_or_dir: Any = None) -> dict[str, float]:
    """Load normalized ensemble weights from manifest or fall back to 40/40/10/10 defaults."""
    if isinstance(manifest_or_dir, dict):
        weights = manifest_or_dir.get("ensemble_weights", {})
    elif isinstance(manifest_or_dir, (str, Path)) and os.path.exists(manifest_or_dir):
        manifest_path = (
            os.path.join(manifest_or_dir, "manifest.json")
            if os.path.isdir(manifest_or_dir)
            else str(manifest_or_dir)
        )
        try:
            with open(manifest_path, encoding="utf-8") as f:
                manifest_data = json.load(f)
            weights = manifest_data.get("ensemble_weights", {})
        except Exception:
            weights = {}
    else:
        weights = {}

    w_rf = float(weights.get("rf", DEFAULT_WEIGHTS["rf"]))
    w_xgb = float(weights.get("xgb", DEFAULT_WEIGHTS["xgb"]))
    w_dt = float(weights.get("dt", DEFAULT_WEIGHTS["dt"]))
    w_iso = float(weights.get("iso", DEFAULT_WEIGHTS["iso"]))

    total = w_rf + w_xgb + w_dt + w_iso
    if total <= 0:
        return dict(DEFAULT_WEIGHTS)
    return {
        "rf": w_rf / total,
        "xgb": w_xgb / total,
        "dt": w_dt / total,
        "iso": w_iso / total,
    }


def risk_score(
    p_HR_rf: float,
    p_HR_xgb: float,
    p_HR_dt: float = 0.0,
    p_iso: float = 0.0,
    weights: dict[str, float] | float = None,
    calibrator: Any = None,
    cal_method: str = "isotonic",
) -> np.ndarray:
    """Compute consensus ensemble risk score across all 4 models, then calibrate."""
    if isinstance(weights, dict):
        w_rf = weights.get("rf", 0.40)
        w_xgb = weights.get("xgb", 0.40)
        w_dt = weights.get("dt", 0.10)
        w_iso = weights.get("iso", 0.10)
    elif isinstance(weights, (int, float)):
        # Backward compatibility for (p_rf, p_xgb, w_rf, calibrator, cal_method)
        w_rf = float(weights)
        w_xgb = 1.0 - w_rf
        w_dt = 0.0
        w_iso = 0.0
    else:
        w_rf, w_xgb, w_dt, w_iso = 0.40, 0.40, 0.10, 0.10

    raw = w_rf * p_HR_rf + w_xgb * p_HR_xgb + w_dt * p_HR_dt + w_iso * p_iso
    if not isinstance(raw, np.ndarray):
        raw = np.array([raw])

    if calibrator is not None:
        try:
            return apply_calibrator(calibrator, cal_method, raw)
        except Exception:
            return raw
    return raw


# Alias per specification
score_risk = risk_score


def model_votes(p_rf, p_xgb, p_dt, iso_flag):
    return {
        "rf_prob": float(p_rf),
        "xgb_prob": float(p_xgb),
        "dt_prob": float(p_dt),
        "iso_flag": bool(iso_flag) if not isinstance(iso_flag, int) else int(iso_flag),
    }


def get_model_scores(features, models, manifest=None) -> dict[str, float]:
    """Extract individual model risk probabilities and normalized anomaly score in [0, 1]."""
    if not isinstance(features, pd.DataFrame):
        features = pd.DataFrame([features])

    scores = {
        "decision_tree": 0.0,
        "random_forest": 0.0,
        "xgboost": 0.0,
        "isolation_forest": 0.0,
    }

    if "decision_tree" in models:
        dt = models["decision_tree"]
        proba = dt.predict_proba(features)
        scores["decision_tree"] = float(proba[:, 2][0]) if proba.shape[1] > 2 else float(proba[:, -1][0])

    if "random_forest" in models:
        rf = models["random_forest"]
        proba = rf.predict_proba(features)
        scores["random_forest"] = float(proba[:, 2][0]) if proba.shape[1] > 2 else float(proba[:, -1][0])

    if "xgboost" in models:
        xgb_m = models["xgboost"]
        proba = xgb_m.predict_proba(features)
        scores["xgboost"] = float(proba[:, 2][0]) if proba.shape[1] > 2 else float(proba[:, -1][0])

    if "isolation_forest" in models:
        iso = models["isolation_forest"]
        raw_score = float(iso.decision_function(features)[0])
        thresh = float(manifest.get("anomaly_threshold", 0.0)) if manifest else 0.0
        # Sigmoid centered at anomaly threshold mapping to [0, 1] risk
        iso_risk = 1.0 / (1.0 + np.exp(5.0 * (raw_score - thresh)))
        scores["isolation_forest"] = float(np.clip(iso_risk, 0.0, 1.0))

    return scores
