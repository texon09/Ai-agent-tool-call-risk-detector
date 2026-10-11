"""Train models."""

import argparse
import datetime
import itertools
import json
import os
import sys

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.model_selection import GroupKFold
from sklearn.tree import DecisionTreeClassifier
from sklearn.utils.class_weight import compute_sample_weight

try:
    from backend.app.ml.calibrate import apply_calibrator, fit_calibrator
    from backend.training.data import CLASS_ORDER, file_sha256, load_feature_list, load_split
    from backend.training.metrics import recall_at_fpr, threshold_at_fpr
except ImportError:
    from app.ml.calibrate import apply_calibrator, fit_calibrator
    from training.data import CLASS_ORDER, file_sha256, load_feature_list, load_split
    from training.metrics import recall_at_fpr, threshold_at_fpr



def get_class_map():
    return {k: v for v, k in enumerate(CLASS_ORDER)}


def run_grid_search(model_class, param_grid, X, y_str, groups, fit_kwargs=None, proba_idx=2):
    y = np.array([get_class_map()[v] for v in y_str])
    best_score = -1.0
    best_params = None

    keys = list(param_grid.keys())
    values = list(param_grid.values())
    combinations = [dict(zip(keys, v, strict=False)) for v in itertools.product(*values)]

    results = []

    for params in combinations:
        gkf = GroupKFold(n_splits=5)
        scores = []
        for train_idx, val_idx in gkf.split(X, y, groups=groups):
            X_tr, y_tr = X.iloc[train_idx], y[train_idx]
            X_v, _y_v = X.iloc[val_idx], y[val_idx]

            model = model_class(**params, random_state=42)
            if fit_kwargs:
                kw = {}
                if "sample_weight" in fit_kwargs:
                    kw["sample_weight"] = compute_sample_weight("balanced", y_tr)
                model.fit(X_tr, y_tr, **kw)
            else:
                model.fit(X_tr, y_tr)

            preds = model.predict_proba(X_v)[:, proba_idx]
            y_v_str = np.array(y_str)[val_idx]
            rec = recall_at_fpr(y_v_str, preds, 0.05)
            scores.append(rec)

        mean_score = np.mean(scores)
        results.append((mean_score, params))

        if mean_score > best_score:
            best_score = mean_score
            best_params = params
        elif mean_score == best_score:
            # tie break - simpler model
            # for DT/RF: lower max_depth or lower n_estimators
            def get_complexity(p):
                c = 0
                if "n_estimators" in p:
                    c += p["n_estimators"]
                if "max_depth" in p:
                    c += (100 if p["max_depth"] is None else p["max_depth"]) * 100
                if "learning_rate" in p:
                    c += p["learning_rate"] * 10
                return c

            if best_params is not None and get_complexity(params) < get_complexity(best_params):
                best_params = params

    return best_params, results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--metrics-dir", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--seeds", nargs="+", type=int, required=True)
    args = parser.parse_args()

    v_dir = os.path.join(args.out_dir, args.version)
    if os.path.exists(v_dir) and os.listdir(v_dir):
        print(f"Error: {v_dir} already exists and is not empty.")
        sys.exit(1)

    os.makedirs(v_dir, exist_ok=True)
    os.makedirs(args.metrics_dir, exist_ok=True)

    features = load_feature_list(args.data_dir)
    tr_path = os.path.join(args.data_dir, "train_features.csv")
    val_path = os.path.join(args.data_dir, "val_features.csv")

    X_tr, y_tr_str, meta_tr = load_split(tr_path, features)
    X_val, y_val_str, meta_val = load_split(val_path, features)

    groups_tr = meta_tr["task_id"].values

    # M1 DT
    dt_grid = {"max_depth": [3, 4, 5, 6], "class_weight": ["balanced"]}
    dt_best, dt_res = run_grid_search(
        DecisionTreeClassifier, dt_grid, X_tr, y_tr_str, groups_tr, proba_idx=2
    )

    # M2 RF
    rf_grid = {
        "n_estimators": [200, 400],
        "max_depth": [6, 8, 12, None],
        "min_samples_leaf": [1, 3],
        "class_weight": ["balanced"],
    }
    rf_best, rf_res = run_grid_search(
        RandomForestClassifier, rf_grid, X_tr, y_tr_str, groups_tr, proba_idx=2
    )

    # M3 XGB
    xgb_grid = {
        "n_estimators": [200, 400],
        "max_depth": [3, 5],
        "learning_rate": [0.05, 0.1],
        "subsample": [0.8],
        "colsample_bytree": [0.8],
        "objective": ["multi:softprob"],
        "num_class": [3],
    }
    xgb_best, xgb_res = run_grid_search(
        xgb.XGBClassifier,
        xgb_grid,
        X_tr,
        y_tr_str,
        groups_tr,
        fit_kwargs={"sample_weight": True},
        proba_idx=2,
    )

    # Store grid results
    with open(os.path.join(args.metrics_dir, "grid_search.json"), "w") as f:
        json.dump({"DT": dt_res, "RF": rf_res, "XGB": xgb_res}, f, indent=2)

    # Isolation Forest on TRAIN SAFE rows
    safe_mask = y_tr_str == "SAFE"
    X_tr_safe = X_tr[safe_mask]

    val_results = []

    for seed in args.seeds:
        dt = DecisionTreeClassifier(**dt_best, random_state=seed)
        y_tr_int = np.array([get_class_map()[v] for v in y_tr_str])
        dt.fit(X_tr, y_tr_int)

        rf = RandomForestClassifier(**rf_best, random_state=seed)
        rf.fit(X_tr, y_tr_int)

        xgb_m = xgb.XGBClassifier(**xgb_best, random_state=seed)
        xgb_m.fit(X_tr, y_tr_int, sample_weight=compute_sample_weight("balanced", y_tr_int))

        iso = IsolationForest(random_state=seed)
        iso.fit(X_tr_safe)

        # VAL evaluation
        p_rf = rf.predict_proba(X_val)[:, 2]
        p_xgb = xgb_m.predict_proba(X_val)[:, 2]

        best_w = 0.0
        best_rec = -1.0
        best_cal = None
        best_cal_method = ""

        for w_rf in [0.0, 0.25, 0.5, 0.75, 1.0]:
            raw = w_rf * p_rf + (1.0 - w_rf) * p_xgb
            cal, method = fit_calibrator(y_val_str, raw)
            cal_scores = apply_calibrator(cal, method, raw)
            rec = recall_at_fpr(y_val_str, cal_scores, 0.05)
            if rec > best_rec:
                best_rec = rec
                best_w = w_rf
                best_cal = cal
                best_cal_method = method

        # Operating points
        raw = best_w * p_rf + (1.0 - best_w) * p_xgb
        cal_scores = apply_calibrator(best_cal, best_cal_method, raw)

        ops = {}
        for fpr_target in [0.01, 0.02, 0.05, 0.10]:
            thresh = threshold_at_fpr(y_val_str, cal_scores, fpr_target)

            safe_val_scores = cal_scores[y_val_str == "SAFE"]
            actual_fpr = (
                float(np.sum(safe_val_scores >= thresh) / len(safe_val_scores))
                if len(safe_val_scores) > 0
                else 0.0
            )

            hr_scores = cal_scores[y_val_str == "HIGH-RISK"]
            rec = float(np.sum(hr_scores >= thresh) / len(hr_scores)) if len(hr_scores) > 0 else 0.0

            susp_scores = cal_scores[y_val_str == "SUSPICIOUS"]
            susp_share = (
                float(np.sum(susp_scores >= thresh) / len(susp_scores))
                if len(susp_scores) > 0
                else 0.0
            )

            ops[f"{fpr_target * 100:.0f}%"] = {
                "threshold": thresh,
                "recall": rec,
                "suspicious_share": susp_share,
                "actual_safe_fpr": actual_fpr,
            }

        # Isolation forest anomaly threshold
        iso_scores = iso.decision_function(X_val)
        safe_iso_scores = iso_scores[y_val_str == "SAFE"]
        # flagged means score < threshold. we want at most 5% flagged, tie-aware
        best_t = -float("inf")
        if len(safe_iso_scores) > 0:
            for t in np.sort(np.unique(safe_iso_scores)):
                if np.sum(safe_iso_scores < t) / len(safe_iso_scores) <= 0.05:
                    best_t = t
                else:
                    break
            iso_thresh = (
                float(best_t) if best_t != -float("inf") else float(np.min(safe_iso_scores))
            )
        else:
            iso_thresh = 0.0

        susp_iso = iso_scores[y_val_str == "SUSPICIOUS"]
        hr_iso = iso_scores[y_val_str == "HIGH-RISK"]

        iso_susp_det = (
            float(np.sum(susp_iso < iso_thresh) / len(susp_iso)) if len(susp_iso) > 0 else 0.0
        )
        iso_hr_det = float(np.sum(hr_iso < iso_thresh) / len(hr_iso)) if len(hr_iso) > 0 else 0.0

        val_results.append(
            {
                "seed": seed,
                "w_rf": best_w,
                "cal_method": best_cal_method,
                "ops": ops,
                "iso_thresh": iso_thresh,
                "iso_susp_det": iso_susp_det,
                "iso_hr_det": iso_hr_det,
            }
        )

        if seed == args.seeds[0]:
            joblib.dump(dt, os.path.join(v_dir, "decision_tree.joblib"))
            joblib.dump(rf, os.path.join(v_dir, "random_forest.joblib"))
            joblib.dump(xgb_m, os.path.join(v_dir, "xgboost.joblib"))
            joblib.dump(iso, os.path.join(v_dir, "isolation_forest.joblib"))
            joblib.dump(best_cal, os.path.join(v_dir, "calibrator.joblib"))

            # features importances
            print("--- RF Top 15 Features ---")
            for idx in np.argsort(rf.feature_importances_)[::-1][:15]:
                print(f"{features[idx]}: {rf.feature_importances_[idx]:.4f}")
            print("--- XGB Top 15 Features ---")
            for idx in np.argsort(xgb_m.feature_importances_)[::-1][:15]:
                print(f"{features[idx]}: {xgb_m.feature_importances_[idx]:.4f}")

            manifest = {
                "version": args.version,
                "feature_names": features,
                "class_order": CLASS_ORDER,
                "ensemble_weights": {"rf": best_w, "xgb": 1.0 - best_w},
                "calibration_method": best_cal_method,
                "thresholds": {
                    "t_medium": None,
                    "t_high": None,
                    "t_confirm": None,
                    "t_block": None,
                },
                "thresholds_note": "fitted later on the full hybrid pipeline",
                "operating_points": ops,
                "anomaly_threshold": iso_thresh,
                "hyperparameters": {"dt": dt_best, "rf": rf_best, "xgb": xgb_best},
                "seeds": args.seeds,
                "sha256": {
                    "train_features.csv": file_sha256(tr_path),
                    "val_features.csv": file_sha256(val_path),
                },
                "row_counts": {"train_features.csv": len(X_tr), "val_features.csv": len(X_val)},
                "test_files": "not used in training",
                "constant_feature_names": [c for c in features if X_tr[c].nunique() <= 1],
                "library_versions": {
                    "numpy": np.__version__,
                    "pandas": pd.__version__,
                    "xgboost": xgb.__version__,
                    "joblib": joblib.__version__,
                },
                "created_at": datetime.datetime.utcnow().isoformat() + "Z",
                "joblib_sha256": {},
            }
            for j in [
                "decision_tree.joblib",
                "random_forest.joblib",
                "xgboost.joblib",
                "isolation_forest.joblib",
                "calibrator.joblib",
            ]:
                manifest["joblib_sha256"][j] = file_sha256(os.path.join(v_dir, j))

            with open(os.path.join(v_dir, "manifest.json"), "w") as f:
                json.dump(manifest, f, indent=2)

            card = {
                "data_description": "Training data for risk detection.",
                "val_metrics": val_results[0],
                "limitations": (
                    "synthetic-data shared assumptions, "
                    "per-call baseline not trainable from plan-level data, "
                    "policy thresholds deferred, 4 constant features, "
                    "many train/test duplicate feature vectors "
                    "and 31 conflicting-label groups"
                ),
            }
            with open(os.path.join(v_dir, "model_card.json"), "w") as f:
                json.dump(card, f, indent=2)

    with open(os.path.join(args.metrics_dir, "val_results.json"), "w") as f:
        json.dump(val_results, f, indent=2)

    print("--- Chosen Hyperparameters ---")
    print(f"DT: {dt_best}")
    print(f"RF: {rf_best}")
    print(f"XGB: {xgb_best}")
    print(f"Ensemble weights: w_rf={val_results[0]['w_rf']}, w_xgb={1.0 - val_results[0]['w_rf']}")
    print(f"Calibration method: {val_results[0]['cal_method']}")
    print(f"Anomaly threshold: {val_results[0]['iso_thresh']}")
    print(
        f"Detection rates (iso): susp={val_results[0]['iso_susp_det']:.2%}, "
        f"hr={val_results[0]['iso_hr_det']:.2%}"
    )
    print("--- VAL metrics (mean/std) ---")
    rec_5 = [r["ops"]["5%"]["recall"] for r in val_results]
    print(f"Recall at 5% FPR: {np.mean(rec_5):.4f} ± {np.std(rec_5):.4f}")
    print("--- Files created ---")
    for fname in os.listdir(v_dir):
        print(f"{fname}: {os.path.getsize(os.path.join(v_dir, fname))} bytes")


if __name__ == "__main__":
    main()
