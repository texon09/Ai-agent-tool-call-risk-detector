"""Ensemble."""


try:
    from app.ml.calibrate import apply_calibrator
except ImportError:
    from backend.app.ml.calibrate import apply_calibrator


def risk_score(p_HR_rf, p_HR_xgb, w_rf, calibrator, cal_method):
    raw = w_rf * p_HR_rf + (1.0 - w_rf) * p_HR_xgb
    import numpy as np

    if not isinstance(raw, np.ndarray):
        raw = np.array([raw])
    return apply_calibrator(calibrator, cal_method, raw)


# Alias per P4 task specification
score_risk = risk_score


def model_votes(p_rf, p_xgb, p_dt, iso_flag):
    return {
        "rf_prob": float(p_rf),
        "xgb_prob": float(p_xgb),
        "dt_prob": float(p_dt),
        "iso_flag": bool(iso_flag) if not isinstance(iso_flag, int) else int(iso_flag),
    }

