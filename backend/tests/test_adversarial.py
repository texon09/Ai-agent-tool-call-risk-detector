"""Adversarial test runner verifying short attack detection across models and policy."""

import json
from pathlib import Path

import pandas as pd
import pytest
from app.features.extractor import FEATURE_NAMES, extract_features
from app.ml.ensemble import get_model_scores, score_risk
from app.ml.loader import load_model
from app.policy.decision import decide
from app.rules.engine import RuleEngine
from app.rules.inspector import ArgumentInspector

ADVERSARIAL_DIR = Path(__file__).resolve().parent / "adversarial"
REPO_ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = REPO_ROOT / "artifacts" / "models" / "v2"

rule_engine = RuleEngine()
inspector = ArgumentInspector()
manifest, models = load_model(str(MODEL_DIR))


def get_adversarial_cases():
    cases = []
    for f in sorted(ADVERSARIAL_DIR.glob("*.json")):
        with open(f, encoding="utf-8") as jf:
            cases.append(json.load(jf))
    return cases


@pytest.mark.parametrize("case", get_adversarial_cases(), ids=lambda c: c["name"])
def test_adversarial_short_attack_detected(case):
    plan = case["plan"]
    expected_action = case["expected_action"]
    min_score = case["expected_risk_score_min"]

    # 1. Feature extraction
    feat_vec = extract_features(plan)
    feat_df = pd.DataFrame([feat_vec], columns=FEATURE_NAMES)

    # 2. ML Scoring
    ind_scores = get_model_scores(feat_df, models, manifest)
    calibrated = score_risk(
        p_HR_rf=ind_scores["random_forest"],
        p_HR_xgb=ind_scores["xgboost"],
        p_HR_dt=ind_scores["decision_tree"],
        p_iso=ind_scores["isolation_forest"],
        weights=manifest.get("ensemble_weights"),
        calibrator=models["calibrator"],
        cal_method=manifest.get("calibration_method", "isotonic"),
    )
    ensemble_score = float(calibrated[0])

    # 3. Rule and inspector execution
    rule_results = rule_engine.evaluate(plan)
    inspector_results = inspector.scan(plan)

    # 4. Policy decision
    policy_result = decide(
        risk_score=ensemble_score,
        rule_results=rule_results,
        inspector_results=inspector_results,
    )

    action = policy_result["action"]

    print(
        f"\n[{case['name']}] Ensemble={ensemble_score:.3f} (DT={ind_scores['decision_tree']:.2f}, "
        f"RF={ind_scores['random_forest']:.2f}, XGB={ind_scores['xgboost']:.2f}, "
        f"ISO={ind_scores['isolation_forest']:.2f}) Action={action} (Crit={policy_result['critical_violations']})"
    )

    assert ensemble_score >= min_score, (
        f"{case['name']}: Expected ensemble score >= {min_score}, got {ensemble_score:.3f}"
    )
    assert action == expected_action, (
        f"{case['name']}: Expected action {expected_action}, got {action}"
    )
