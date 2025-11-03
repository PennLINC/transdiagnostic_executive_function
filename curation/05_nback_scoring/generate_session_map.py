#!/usr/bin/env python3
"""
Generate a mapping of scanid -> BIDS session_id (ses-1/2/3, ...)
by scanning a Flywheel-style directory tree and ordering sessions
chronologically by their created timestamps.

Input tree (per subject):
  <bblid>/SESSIONS/<scanid>/(...)
  with metadata at <scanid>.flywheel.json containing created timestamp:
    {"created": {"$date": "..."}} or {"created": "..."}

Output TSV columns:
  bblid\tscanid\tsession_id\ttimestamp

Example:
  python /cbica/projects/executive_function/code/curation/cubids_curation/generate_session_map.py \
    --flywheel-dir /cbica/projects/executive_function/data/bids/sourcedata/EFR01/SUBJECTS \
    --output /cbica/projects/executive_function/task_events_files/session_map.tsv
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export scanid->session_id mapping from a Flywheel directory with timestamps"
    )
    parser.add_argument(
        "--flywheel-dir",
        required=True,
        type=Path,
        help="Root Flywheel SUBJECTS directory (contains <bblid>/SESSIONS/<scanid>)",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Path to write mapping TSV (columns: bblid, scanid, session_id, timestamp)",
    )
    return parser.parse_args()


def load_session_timestamp(scan_root: Path, scanid: str) -> Optional[pd.Timestamp]:
    json_path = scan_root / f"{scanid}.flywheel.json"
    if not json_path.exists():
        return None
    try:
        with open(json_path, "r") as fp:
            meta = json.load(fp)
        timestamp = meta.get("timestamp")
        if not timestamp:
            return None
        return pd.to_datetime(timestamp, utc=True, errors="coerce")
    except Exception:
        return None


def discover_subject_scanids(flywheel_dir: Path) -> Dict[str, List[str]]:
    subject_to_scanids: Dict[str, List[str]] = {}
    # Walk subjects; expect subjects as immediate children directories
    for subj_dir in flywheel_dir.iterdir():
        if not subj_dir.is_dir():
            continue
        bblid = subj_dir.name
        sessions_dir = subj_dir / "SESSIONS"
        if not sessions_dir.is_dir():
            continue
        for scan_dir in sessions_dir.iterdir():
            if not scan_dir.is_dir():
                continue
            scanid = scan_dir.name
            subject_to_scanids.setdefault(bblid, []).append(scanid)
    return subject_to_scanids


def build_session_mapping(
    flywheel_dir: Path, subject_to_scanids: Dict[str, List[str]]
) -> List[Tuple[str, str, str]]:
    rows: List[Tuple[str, str, str]] = []
    for bblid, scanids in subject_to_scanids.items():
        dated: List[Tuple[str, Optional[pd.Timestamp]]] = []
        for scanid in scanids:
            scan_root = flywheel_dir / bblid / "SESSIONS" / scanid
            ts = load_session_timestamp(scan_root, scanid)
            dated.append((scanid, ts))
        # Sort by timestamp (None/NaT last), then by scanid
        dated.sort(key=lambda x: (x[1] is None or pd.isna(x[1]), x[1], x[0]))
        for idx, (scanid, _ts) in enumerate(dated, start=1):
            rows.append((bblid, scanid, f"ses-{idx}", _ts))
    return rows


def main() -> int:
    args = parse_args()
    flywheel_dir: Path = args.flywheel_dir
    output_path: Path = args.output

    subject_to_scanids = discover_subject_scanids(flywheel_dir)
    mapping_rows = build_session_mapping(flywheel_dir, subject_to_scanids)

    df = pd.DataFrame(
        mapping_rows, columns=["bblid", "scanid", "session_id", "timestamp"]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, sep="\t", index=False)
    print(f"Wrote session map to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
