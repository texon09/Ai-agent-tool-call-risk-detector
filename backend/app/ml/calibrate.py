"""Calibrator."""

import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression


def fit_calibrator(y_val, raw_scores):
    """Fit calibrator."""
    y_binary = (y_val == "HIGH-RISK").astype(int)
    n_high = np.sum(y_binary == 1)
    n_rest = np.sum(y_binary == 0)

    if n_high >= 100 and n_rest >= 100:
        method = "isotonic"
        cal = IsotonicRegression(out_of_bounds="clip")
        cal.fit(raw_scores, y_binary)
    else:
        method = "platt"
        cal = LogisticRegression()
        cal.fit(raw_scores.reshape(-1, 1), y_binary)
    return cal, method


def apply_calibrator(calibrator, method, raw_scores):
    if method == "isotonic":
        return calibrator.predict(raw_scores)
    else:
        return calibrator.predict_proba(raw_scores.reshape(-1, 1))[:, 1]
