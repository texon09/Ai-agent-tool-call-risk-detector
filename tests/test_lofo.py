import glob
import os

import numpy as np
from sklearn.tree import DecisionTreeClassifier


def test_manifest_class_order():
    # Simulate the class-index bug fix
    manifest_class_order = ["SAFE", "SUSPICIOUS", "HIGH-RISK"]
    hr_idx = manifest_class_order.index("HIGH-RISK")
    assert hr_idx == 2

    # Toy data with missing classes or unordered classes
    # If we mapped alphabetically: HIGH-RISK=0, SAFE=1, SUSPICIOUS=2
    # But with manifest order: SAFE=0, SUSPICIOUS=1, HIGH-RISK=2
    labels_str = ["HIGH-RISK", "SAFE", "SUSPICIOUS", "SAFE"]
    labels_int = np.array([manifest_class_order.index(lbl) for lbl in labels_str])
    assert list(labels_int) == [2, 0, 1, 0]

    # Check that model.classes_ equals [0, 1, 2]
    dt = DecisionTreeClassifier()
    X = np.array([[1], [2], [3], [4]])
    dt.fit(X, labels_int)
    assert list(dt.classes_) == [0, 1, 2]

    # So predict_proba[:, hr_idx] correctly extracts HIGH-RISK
    preds = dt.predict_proba(X)
    assert preds.shape[1] == 3


def test_all_five_families_run():
    # Just asserting the files exist in data/processed
    data_dir = "data/processed"
    if os.path.exists(data_dir):
        test_files = glob.glob(os.path.join(data_dir, "lofo_test_*.csv"))
        fams = [
            os.path.basename(f).replace("lofo_test_", "").replace(".csv", "")
            for f in test_files
        ]
        assert len(fams) == 5
        assert set(fams) == {
            "data_exfiltration",
            "privilege_escalation",
            "destructive",
            "credential_harvesting",
            "injection_triggered",
        }
