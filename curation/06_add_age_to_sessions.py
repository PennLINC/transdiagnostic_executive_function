#!/usr/bin/env python3
import argparse
import glob
import json
import os
from collections import OrderedDict

import pandas as pd

AGE_DESC = "age in fractional years at the time of each session"


def load_age_map(age_csv_path: str) -> dict:
    """
    EF_age_info.csv columns:
      participant_id  (numeric, e.g., 20139)
      session_id      (numeric, e.g., 1, 2, 3)
      age             (float)
    """
    df = pd.read_csv(age_csv_path)
    m = {}
    for _, r in df.iterrows():
        pid = f"sub-{int(r['participant_id'])}"
        sid = f"ses-{int(r['session_id'])}"
        m[(pid, sid)] = r["age"]
    return m


def update_tsv(tsv_path: str, age_map: dict, dry_run: bool) -> int:
    """
    Insert 'age' as the 2nd column after 'session_id'.
    Returns number of missing ages (written as 'n/a').
    """
    subj = os.path.basename(tsv_path).split("_sessions.tsv")[0]  # e.g., sub-20139

    # Key change: preserve literal strings like "n/a" and don't convert them to NaN
    df = pd.read_csv(
        tsv_path,
        sep="\t",
        dtype=str,
        keep_default_na=False,
        na_filter=False,
    )

    ages = []
    missing = 0
    for sid in df["session_id"].astype(str).tolist():
        key = (subj, sid)  # sid already like 'ses-1'
        if key in age_map:
            ages.append(str(age_map[key]))
        else:
            ages.append("n/a")
            missing += 1

    insert_at = list(df.columns).index("session_id") + 1
    df.insert(insert_at, "age", ages)

    if not dry_run:
        # Key change: write any actual missing values as "n/a" instead of blanks
        df.to_csv(
            tsv_path,
            sep="\t",
            index=False,
            lineterminator="\n",
            na_rep="n/a",
        )

    return missing


def update_json(json_path: str, dry_run: bool):
    """
    Insert 'age' as 2nd key after 'session_id' with the requested Description.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f, object_pairs_hook=OrderedDict)

    new_data = OrderedDict()
    new_data["session_id"] = data["session_id"]
    new_data["age"] = OrderedDict([("Description", AGE_DESC)])

    for k, v in data.items():
        if k != "session_id":
            new_data[k] = v

    if not dry_run:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(new_data, f, indent=2)
            f.write("\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bids-root", required=True)
    ap.add_argument("--age-file", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    age_map = load_age_map(args.age_file)

    tsvs = sorted(glob.glob(os.path.join(args.bids_root, "sub-*", "sub-*_sessions.tsv")))
    if not tsvs:
        raise SystemExit("No sub-*/sub-*_sessions.tsv files found under bids root.")

    print("DRY RUN" if args.dry_run else "APPLY")
    print(f"Found {len(tsvs)} sessions.tsv files\n")

    total_missing = 0
    for tsv_path in tsvs:
        subj_dir = os.path.dirname(tsv_path)
        subj = os.path.basename(tsv_path).split("_sessions.tsv")[0]
        json_path = os.path.join(subj_dir, f"{subj}_sessions.json")

        missing = update_tsv(tsv_path, age_map, args.dry_run)
        total_missing += missing

        if os.path.exists(json_path):
            update_json(json_path, args.dry_run)

        print(f"{subj}: missing_age={missing}")

    print(f"\nTotal missing ages (written as n/a): {total_missing}")
    if args.dry_run:
        print("Dry run complete. Re-run without --dry-run to apply.")


if __name__ == "__main__":
    main()

