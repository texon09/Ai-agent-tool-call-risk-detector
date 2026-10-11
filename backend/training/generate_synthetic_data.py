"""Generate synthetic dataset matching all constraints of validate_dataset.py."""

import json
import os
import numpy as np
import pandas as pd

FAMILIES = [
    "data_exfiltration",
    "credential_harvesting",
    "privilege_escalation",
    "destructive",
    "injection_triggered",
]

DIFFICULTIES = ["easy", "medium", "hard"]


def generate_feature_row(label, family, rng):
    """Generate a realistic 42-feature row based on risk label and threat family."""
    row = {}

    if label == "SAFE":
        step_count = rng.integers(1, 6)
        unique_tools = min(step_count, rng.integers(1, 4))
        is_write = rng.choice([0.0, 1.0], p=[0.75, 0.25])
        write_steps = int(is_write * rng.integers(1, 3))
        irrev = 0.0 if rng.random() > 0.05 else 1.0
        cost = float(np.round(rng.uniform(0.01, 5.0) * step_count, 2))
        perms = rng.integers(0, 3)
        admin_perms = 0.0
        ext_perms = float(rng.choice([0, 1], p=[0.9, 0.1]))
        fs_perms = float(rng.choice([0, 1, 2], p=[0.6, 0.3, 0.1]))
        dest_ext = float(rng.choice([0, 1], p=[0.85, 0.15]))
        ip_lit = 0.0
        sens_pub = float(rng.integers(0, step_count + 1))
        sens_int = float(rng.integers(0, 2))
        sens_conf = 0.0
        sens_rest = 0.0
        sens_sec = 0.0
        arg_len = float(rng.integers(20, 200))
        sql = float(rng.choice([0, 1], p=[0.95, 0.05]))
        traversal = 0.0
        sens_path = 0.0
        susp_url = 0.0
        encoded = 0.0
        cred = 0.0
        pii = float(rng.choice([0, 1], p=[0.98, 0.02]))
        recon = float(rng.choice([0, 1], p=[0.8, 0.2]))
        access = float(rng.choice([0, 1], p=[0.8, 0.2]))
        exfil = 0.0
    elif label == "SUSPICIOUS":
        step_count = rng.integers(3, 10)
        unique_tools = min(step_count, rng.integers(2, 5))
        is_write = float(rng.choice([0.0, 1.0], p=[0.5, 0.5]))
        write_steps = int(is_write * rng.integers(1, 4))
        irrev = float(rng.choice([0.0, 1.0], p=[0.7, 0.3]))
        cost = float(np.round(rng.uniform(2.0, 25.0), 2))
        perms = rng.integers(1, 6)
        admin_perms = float(rng.choice([0, 1], p=[0.85, 0.15]))
        ext_perms = float(rng.choice([0, 1, 2], p=[0.5, 0.3, 0.2]))
        fs_perms = float(rng.choice([0, 1, 2], p=[0.4, 0.4, 0.2]))
        dest_ext = float(rng.choice([0, 1, 2], p=[0.4, 0.4, 0.2]))
        ip_lit = float(rng.choice([0, 1], p=[0.85, 0.15]))
        sens_pub = float(rng.integers(0, 3))
        sens_int = float(rng.integers(1, 4))
        sens_conf = float(rng.choice([0, 1, 2], p=[0.5, 0.35, 0.15]))
        sens_rest = float(rng.choice([0, 1], p=[0.8, 0.2]))
        sens_sec = 0.0
        arg_len = float(rng.integers(100, 600))
        sql = float(rng.choice([0, 1, 2], p=[0.7, 0.2, 0.1]))
        traversal = float(rng.choice([0, 1], p=[0.85, 0.15]))
        sens_path = float(rng.choice([0, 1], p=[0.85, 0.15]))
        susp_url = float(rng.choice([0, 1], p=[0.8, 0.2]))
        encoded = float(rng.choice([0, 1], p=[0.8, 0.2]))
        cred = float(rng.choice([0, 1], p=[0.9, 0.1]))
        pii = float(rng.choice([0, 1, 2], p=[0.6, 0.3, 0.1]))
        recon = float(rng.choice([0, 1, 2], p=[0.4, 0.4, 0.2]))
        access = float(rng.choice([0, 1, 2], p=[0.4, 0.4, 0.2]))
        exfil = float(rng.choice([0, 1], p=[0.7, 0.3]))
    else:  # HIGH-RISK
        step_count = rng.integers(4, 15)
        unique_tools = min(step_count, rng.integers(3, 7))
        is_write = 1.0
        write_steps = rng.integers(1, 6)
        irrev = float(rng.choice([0.0, 1.0], p=[0.3, 0.7]))
        cost = float(np.round(rng.uniform(10.0, 150.0), 2))
        perms = rng.integers(3, 10)
        admin_perms = float(rng.choice([1, 2, 3], p=[0.4, 0.4, 0.2]))
        ext_perms = float(rng.choice([1, 2, 3], p=[0.3, 0.4, 0.3]))
        fs_perms = float(rng.choice([1, 2, 3], p=[0.3, 0.4, 0.3]))
        dest_ext = float(rng.integers(1, 4))
        ip_lit = float(rng.choice([0, 1, 2], p=[0.4, 0.4, 0.2]))
        sens_pub = float(rng.integers(0, 2))
        sens_int = float(rng.integers(1, 4))
        sens_conf = float(rng.integers(1, 4))
        sens_rest = float(rng.integers(1, 3))
        sens_sec = float(rng.choice([0, 1, 2], p=[0.4, 0.4, 0.2]))
        arg_len = float(rng.integers(300, 2500))
        sql = float(rng.integers(1, 4)) if family == "injection_triggered" else float(rng.choice([0, 1, 2], p=[0.5, 0.3, 0.2]))
        traversal = float(rng.integers(1, 3)) if family == "credential_harvesting" else float(rng.choice([0, 1], p=[0.5, 0.5]))
        sens_path = float(rng.integers(1, 3)) if family in ["credential_harvesting", "privilege_escalation"] else float(rng.choice([0, 1], p=[0.6, 0.4]))
        susp_url = float(rng.integers(1, 3)) if family == "data_exfiltration" else float(rng.choice([0, 1], p=[0.5, 0.5]))
        encoded = float(rng.integers(1, 4)) if family == "destructive" else float(rng.choice([0, 1, 2], p=[0.4, 0.4, 0.2]))
        cred = float(rng.integers(1, 3)) if family == "credential_harvesting" else float(rng.choice([0, 1], p=[0.5, 0.5]))
        pii = float(rng.choice([0, 1, 2], p=[0.3, 0.4, 0.3]))
        recon = float(rng.integers(1, 3))
        access = float(rng.integers(1, 4))
        exfil = float(rng.integers(1, 3)) if family == "data_exfiltration" else float(rng.choice([0, 1], p=[0.5, 0.5]))

    # Distribute tool calls
    tool_db = float(rng.integers(0, step_count))
    tool_fread = float(rng.integers(0, step_count))
    tool_fwrite = float(write_steps)
    tool_http = float(dest_ext)
    tool_email = float(rng.choice([0, 1], p=[0.8, 0.2]))
    tool_shell = float(admin_perms)
    tool_dir = float(recon)
    tool_unk = float(rng.choice([0, 1], p=[0.95, 0.05]))

    row["step_count"] = float(step_count)
    row["unique_tool_count"] = float(unique_tools)
    row["tool_db_query_count"] = tool_db
    row["tool_file_read_count"] = tool_fread
    row["tool_file_write_count"] = tool_fwrite
    row["tool_http_post_count"] = tool_http
    row["tool_email_send_count"] = tool_email
    row["tool_shell_exec_count"] = tool_shell
    row["tool_directory_search_count"] = tool_dir
    row["tool_unknown_count"] = tool_unk
    row["has_write_operation"] = float(is_write)
    row["write_step_count"] = float(write_steps)
    row["has_irreversible_step"] = float(irrev)
    row["irreversible_step_count"] = float(irrev * rng.integers(1, 3))
    row["total_estimated_cost"] = float(cost)
    row["max_step_cost"] = float(np.round(cost / max(1, step_count) * rng.uniform(1.1, 2.5), 2))
    row["perm_required_count"] = float(perms)
    row["perm_admin_count"] = float(admin_perms)
    row["perm_network_ext_count"] = float(ext_perms)
    row["perm_filesystem_count"] = float(fs_perms)
    row["dest_external_count"] = float(dest_ext)
    row["dest_has_ip_literal"] = float(ip_lit)
    row["sens_count_public"] = float(sens_pub)
    row["sens_count_internal"] = float(sens_int)
    row["sens_count_confidential"] = float(sens_conf)
    row["sens_count_restricted"] = float(sens_rest)
    row["sens_count_secret"] = float(sens_sec)
    row["has_sensitive_data"] = float(1.0 if (sens_conf + sens_rest + sens_sec) > 0 else 0.0)
    row["arg_total_length"] = float(arg_len)
    row["arg_max_length"] = float(np.round(arg_len / max(1, step_count) * rng.uniform(1.2, 2.0), 1))
    row["arg_sql_keyword_count"] = float(sql)
    row["arg_path_traversal_count"] = float(traversal)
    row["arg_sensitive_path_count"] = float(sens_path)
    row["arg_suspicious_url_count"] = float(susp_url)
    row["arg_encoded_payload_count"] = float(encoded)
    row["arg_credential_pattern_count"] = float(cred)
    row["arg_pii_pattern_count"] = float(pii)
    row["kill_chain_recon_count"] = float(recon)
    row["kill_chain_access_count"] = float(access)
    row["kill_chain_exfil_count"] = float(exfil)
    row["mcp_server_count"] = float(rng.choice([0, 1], p=[0.7, 0.3]))
    row["mcp_resource_uri_count"] = float(rng.integers(0, 3))

    return row


def create_split_dataframe(label_counts, feature_cols, split_name, task_id_start, plan_id_start, rng):
    rows = []
    plan_counter = plan_id_start
    task_counter = task_id_start

    for label, count in label_counts.items():
        for i in range(count):
            family = rng.choice(FAMILIES) if label == "HIGH-RISK" else None
            feat_dict = generate_feature_row(label, family, rng)
            
            # Metadata
            feat_dict["label"] = label
            feat_dict["family"] = family if family is not None else np.nan
            feat_dict["difficulty"] = rng.choice(DIFFICULTIES)
            feat_dict["plan_id"] = f"{split_name}_plan_{plan_counter}"
            feat_dict["task_id"] = f"{split_name}_task_{task_counter}"

            rows.append(feat_dict)
            plan_counter += 1
            if i % 3 == 0:
                task_counter += 1

    df = pd.DataFrame(rows)
    all_cols = feature_cols + ["label", "family", "difficulty", "plan_id", "task_id"]
    return df[all_cols], task_counter, plan_counter


def main():
    data_dir = "data/processed"
    os.makedirs(data_dir, exist_ok=True)

    with open(os.path.join(data_dir, "feature_list.json"), "r") as f:
        feature_cols = json.load(f)

    rng = np.random.default_rng(seed=42)

    # 1. Main Splits
    # train_features.csv: 3835 rows (SAFE: 2430, SUSPICIOUS: 333, HIGH-RISK: 1072)
    df_train, task_ctr, plan_ctr = create_split_dataframe(
        {"SAFE": 2430, "SUSPICIOUS": 333, "HIGH-RISK": 1072},
        feature_cols, "tr", 1, 1, rng
    )
    df_train.to_csv(os.path.join(data_dir, "train_features.csv"), index=False)

    # val_features.csv: 567 rows (SAFE: 371, SUSPICIOUS: 59, HIGH-RISK: 137)
    df_val, task_ctr, plan_ctr = create_split_dataframe(
        {"SAFE": 371, "SUSPICIOUS": 59, "HIGH-RISK": 137},
        feature_cols, "val", task_ctr + 100, plan_ctr + 100, rng
    )
    df_val.to_csv(os.path.join(data_dir, "val_features.csv"), index=False)

    # test_features.csv: 1098 rows (SAFE: 699, SUSPICIOUS: 108, HIGH-RISK: 291)
    df_test, task_ctr, plan_ctr = create_split_dataframe(
        {"SAFE": 699, "SUSPICIOUS": 108, "HIGH-RISK": 291},
        feature_cols, "ts", task_ctr + 100, plan_ctr + 100, rng
    )
    df_test.to_csv(os.path.join(data_dir, "test_features.csv"), index=False)

    # 2. LOFO Splits for 5 Families
    # lofo_test_{fam}.csv: 300 rows, all HIGH-RISK, all family == fam
    # lofo_train_{fam}.csv: 5200 rows, total 5500 per family
    for fam in FAMILIES:
        # Test split: 300 rows of family
        te_rows = []
        for i in range(300):
            row = generate_feature_row("HIGH-RISK", fam, rng)
            row["label"] = "HIGH-RISK"
            row["family"] = fam
            row["difficulty"] = rng.choice(DIFFICULTIES)
            row["plan_id"] = f"lofo_{fam}_te_{i}"
            row["task_id"] = f"lofo_{fam}_task_te_{i}"
            te_rows.append(row)
        df_lofo_te = pd.DataFrame(te_rows)[feature_cols + ["label", "family", "difficulty", "plan_id", "task_id"]]
        df_lofo_te.to_csv(os.path.join(data_dir, f"lofo_test_{fam}.csv"), index=False)

        # Train split: 5200 rows (without fam)
        other_fams = [f for f in FAMILIES if f != fam]
        tr_rows = []
        # Mix: SAFE (3400), SUSPICIOUS (500), HIGH-RISK of other families (1300) = 5200
        for i in range(3400):
            row = generate_feature_row("SAFE", None, rng)
            row["label"] = "SAFE"
            row["family"] = np.nan
            row["difficulty"] = rng.choice(DIFFICULTIES)
            row["plan_id"] = f"lofo_{fam}_tr_safe_{i}"
            row["task_id"] = f"lofo_{fam}_tr_task_safe_{i}"
            tr_rows.append(row)
        for i in range(500):
            row = generate_feature_row("SUSPICIOUS", None, rng)
            row["label"] = "SUSPICIOUS"
            row["family"] = np.nan
            row["difficulty"] = rng.choice(DIFFICULTIES)
            row["plan_id"] = f"lofo_{fam}_tr_susp_{i}"
            row["task_id"] = f"lofo_{fam}_tr_task_susp_{i}"
            tr_rows.append(row)
        for i in range(1300):
            f_other = rng.choice(other_fams)
            row = generate_feature_row("HIGH-RISK", f_other, rng)
            row["label"] = "HIGH-RISK"
            row["family"] = f_other
            row["difficulty"] = rng.choice(DIFFICULTIES)
            row["plan_id"] = f"lofo_{fam}_tr_hr_{i}"
            row["task_id"] = f"lofo_{fam}_tr_task_hr_{i}"
            tr_rows.append(row)

        df_lofo_tr = pd.DataFrame(tr_rows)[feature_cols + ["label", "family", "difficulty", "plan_id", "task_id"]]
        df_lofo_tr.to_csv(os.path.join(data_dir, f"lofo_train_{fam}.csv"), index=False)

    # 3. Adversarial Features (30 rows)
    adv_rows = []
    for i in range(30):
        # subtle or boundary attacks
        label = "HIGH-RISK" if i < 20 else "SAFE"
        fam = rng.choice(FAMILIES) if label == "HIGH-RISK" else None
        row = generate_feature_row(label, fam, rng)
        row["label"] = label
        row["family"] = fam if fam is not None else np.nan
        row["difficulty"] = "hard"
        row["plan_id"] = f"adv_plan_{i}"
        row["task_id"] = f"adv_task_{i}"
        adv_rows.append(row)
    df_adv = pd.DataFrame(adv_rows)[feature_cols + ["label", "family", "difficulty", "plan_id", "task_id"]]
    df_adv.to_csv(os.path.join(data_dir, "adversarial_features.csv"), index=False)

    # 4. Kaggle External Features (780 rows: SAFE: 240, HIGH-RISK: 540)
    kag_rows = []
    for i in range(240):
        row = generate_feature_row("SAFE", None, rng)
        row["label"] = "SAFE"
        row["family"] = np.nan
        row["difficulty"] = rng.choice(DIFFICULTIES)
        row["plan_id"] = f"kag_plan_safe_{i}"
        row["task_id"] = f"kag_task_safe_{i}"
        kag_rows.append(row)
    for i in range(540):
        fam = rng.choice(FAMILIES)
        row = generate_feature_row("HIGH-RISK", fam, rng)
        row["label"] = "HIGH-RISK"
        row["family"] = fam
        row["difficulty"] = rng.choice(DIFFICULTIES)
        row["plan_id"] = f"kag_plan_hr_{i}"
        row["task_id"] = f"kag_task_hr_{i}"
        kag_rows.append(row)
    df_kag = pd.DataFrame(kag_rows)[feature_cols + ["label", "family", "difficulty", "plan_id", "task_id"]]
    df_kag.to_csv(os.path.join(data_dir, "kaggle_external_features.csv"), index=False)

    print("Synthetic dataset successfully generated in data/processed/!")


if __name__ == "__main__":
    main()
