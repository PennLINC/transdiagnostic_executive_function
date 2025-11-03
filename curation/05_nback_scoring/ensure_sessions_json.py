#!/usr/bin/env python3
"""
Ensure each subject with a sessions.tsv has a minimal sessions.json sidecar.

What it does:
- Scans a BIDS directory for subject folders named sub-*
- For each subject, if <subj>/<subj>_sessions.tsv exists and
  <subj>/<subj>_sessions.json does not, create the JSON sidecar with only:
  - session_id: Description text
  - acq_time: Description text

Usage example:
  python curation/cubids_curation/ensure_sessions_json.py \
    --bids-dir /path/to/bids
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Scan BIDS directory; create minimal sub-<id>_sessions.json if missing."
        )
    )
    parser.add_argument(
        "--bids-dir",
        required=True,
        type=Path,
        help="Path to BIDS root containing sub-* directories",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without writing any files",
    )
    return parser.parse_args()


def minimal_sessions_sidecar() -> Dict[str, Dict[str, str]]:
    """Return the minimal sessions.json structure for session_id and acq_time."""
    return {
        "session_id": {
            "Description": (
                "BIDS session label assigned chronologically via Flywheel created timestamp"
            )
        },
        "acq_time": {
            "Description": (
                "Acquisition time for the session rounded to the nearest hour and half-month period for anonymization"
            )
        },
    }


def ensure_subject_sessions_json(subject_dir: Path, dry_run: bool = False) -> bool:
    """
    Create <subj>/<subj>_sessions.json if <subj>/<subj>_sessions.tsv exists
    and the JSON sidecar is missing.

    Returns True if a file was created (or would be, in dry-run); False otherwise.
    """
    if not subject_dir.is_dir():
        return False

    subject_label = subject_dir.name  # e.g., sub-12345
    sessions_tsv = subject_dir / f"{subject_label}_sessions.tsv"
    sessions_json = subject_dir / f"{subject_label}_sessions.json"

    if not sessions_tsv.exists():
        return False
    if sessions_json.exists():
        return False

    if dry_run:
        print(f"Would create: {sessions_json}")
        return True

    sidecar = minimal_sessions_sidecar()
    sessions_json.write_text(json.dumps(sidecar, indent=2) + "\n", encoding="utf-8")
    print(f"Created: {sessions_json}")
    return True


def main() -> int:
    args = parse_args()
    bids_dir: Path = args.bids_dir

    if not bids_dir.exists() or not bids_dir.is_dir():
        print(f"BIDS directory not found or not a directory: {bids_dir}")
        return 1

    created_count = 0
    for subject_dir in sorted(bids_dir.glob("sub-*")):
        try:
            if ensure_subject_sessions_json(subject_dir, dry_run=args.dry_run):
                created_count += 1
        except Exception as exc:
            print(f"Error processing {subject_dir}: {exc}")
            continue

    if args.dry_run:
        print(f"Dry-run complete. Would create {created_count} sessions.json file(s).")
    else:
        print(f"Done. Created {created_count} sessions.json file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
