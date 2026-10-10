"""Ensemble."""


def risk_score(p_HR_rf, p_HR_xgb, w_rf, calibrator, cal_method):
    from backend.app.ml.calibrate import apply_calibrator

    raw = w_rf * p_HR_rf + (1.0 - w_rf) * p_HR_xgb
    import numpy as np

    if not isinstance(raw, np.ndarray):
        raw = np.array([raw])
    return apply_calibrator(calibrator, cal_method, raw)


def model_votes(p_rf, p_xgb, p_dt, iso_flag):
    return {
        "rf_prob": float(p_rf),
        "xgb_prob": float(p_xgb),
        "dt_prob": float(p_dt),
        "iso_flag": iso_flag,
    }
