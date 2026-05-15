#!/usr/bin/env python3

from pathlib import Path
import re
import pandas as pd
from statistics import NormalDist

ROOT = Path("/cbica/projects/executive_function/data/bids/EF_bids_data_DataLad")
OUTDIR = Path("/cbica/projects/executive_function/code/task_contrast/final/behavioral")
OUTFILE = OUTDIR / "nback_block_performance_summary.tsv"

TASK_TYPES = {"0BACK", "2BACK"}

def parse_sub_ses(path):
    m = re.search(r"(sub-[^_/]+)_(ses-[^_/]+)_task-nback", path.name)
    if not m:
        return None, None
    return m.group(1), m.group(2)

def corrected_rate(numerator, denominator):
    if denominator == 0:
        return float("nan")
    return (numerator + 0.5) / (denominator + 1)

def dprime(tp, fn, fp, tn):
    n_targets = tp + fn
    n_nontargets = fp + tn

    if n_targets == 0 or n_nontargets == 0:
        return float("nan")

    hit_rate = corrected_rate(tp, n_targets)
    fa_rate = corrected_rate(fp, n_nontargets)

    z = NormalDist().inv_cdf
    return z(hit_rate) - z(fa_rate)

def add_block_numbers(df):
    condition_counts = {"0BACK": 0, "2BACK": 0}
    current_condition = None
    current_block_label = None
    labels = []

    for trial_type in df["trial_type"]:
        if trial_type in TASK_TYPES:
            if current_condition != trial_type:
                condition_counts[trial_type] += 1
                current_condition = trial_type
                current_block_label = (
                    f"{trial_type.lower()}_{condition_counts[trial_type]:03d}"
                )
            labels.append(current_block_label)
        else:
            current_condition = None
            current_block_label = None
            labels.append(pd.NA)

    df = df.copy()
    df["block_label"] = labels
    return df

def summarize_file(path):
    sub, ses = parse_sub_ses(path)

    df = pd.read_csv(path, sep="\t", dtype=str)
    df = add_block_numbers(df)

    row = {
        "subject": sub,
        "session": ses,
        "events_file": str(path),
    }

    task_df = df[df["trial_type"].isin(TASK_TYPES)].copy()

    for block_label, block in task_df.groupby("block_label", sort=False):
        score = block["score"].fillna("n/a")

        tp = int((score == "true_positive").sum())
        tn = int((score == "true_negative").sum())
        fp = int((score == "false_positive").sum())
        fn = int((score == "false_negative").sum())

        correct = tp + tn
        incorrect = fp + fn
        n_targets = tp + fn

        false_negative_rate = fn / n_targets if n_targets > 0 else float("nan")

        row[f"{block_label}_false_negative_rate"] = false_negative_rate
        row[f"{block_label}_correct"] = correct
        row[f"{block_label}_incorrect"] = incorrect
        row[f"{block_label}_hits"] = tp
        row[f"{block_label}_false_alarm"] = fp
        row[f"{block_label}_dprime"] = dprime(tp, fn, fp, tn)

    return row

def main():
    files = sorted(ROOT.glob("sub-*/ses-*/func/*_task-nback_*_events.tsv"))

    rows = []
    for f in files:
        try:
            rows.append(summarize_file(f))
        except Exception as e:
            print(f"WARNING: failed on {f}: {e}")

    out = pd.DataFrame(rows)

    metric_cols = [
        c for c in out.columns
        if c not in {"subject", "session", "events_file"}
    ]

    for c in metric_cols:
        out[c] = pd.to_numeric(out[c], errors="coerce")

    avg = {
        "subject": "average",
        "session": "average",
        "events_file": "average",
    }

    for c in metric_cols:
        avg[c] = out[c].mean(skipna=True)

    out = pd.concat([out, pd.DataFrame([avg])], ignore_index=True)

    OUTDIR.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUTFILE, sep="\t", index=False)

    print(f"Wrote: {OUTFILE}")
    print(f"Processed {len(rows)} events.tsv files")

if __name__ == "__main__":
    main()
