#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

"""
This script organizes the files for multi-echo gradient-recalled echo sequence for QSM so that it is BIDS valid (moves from swi to anat folder and renames files with appropriate naming).
"""

def decide_part_from_imagetype(image_type_list):
    """
    Decide 'mag' or 'phase' based on ImageType list.
    Returns 'mag', 'phase', or None if undecidable.
    """
    if not isinstance(image_type_list, list):
        return None
    # Normalize to upper strings without whitespace
    items = {str(x).strip().upper() for x in image_type_list}
    if "M" in items:
        return "mag"
    if "P" in items:
        return "phase"
    return None

def transform_basename(old_stem, part_kind):
    """
    Given a BIDS-ish base filename stem (no extension), e.g.
        sub-23698_ses-1_run-01_echo-1_qsm
    return the new stem:
        sub-23698_ses-1_echo-1_part-mag_MEGRE
    Rules:
      - remove any token starting with 'run-'
      - insert 'part-<mag|phase>' immediately after the 'echo-*' token
      - replace the last token with 'MEGRE'
    Preserve any other entities (e.g., acq-*, dir-*, rec-*, etc.) in their original order.
    """
    tokens = old_stem.split('_')
    # Drop any run-* tokens
    tokens = [t for t in tokens if not t.startswith('run-')]

    # Find echo-* index
    echo_idx = None
    for i, t in enumerate(tokens):
        if t.startswith('echo-'):
            echo_idx = i
            break

    if echo_idx is None:
        # No echo token found; we’ll just append part- and proceed
        insert_idx = len(tokens) - 1
    else:
        insert_idx = echo_idx + 1

    # Insert part-<kind> (avoid duplicating if already present somehow)
    part_token = f"part-{part_kind}"
    if part_token not in tokens:
        tokens.insert(insert_idx, part_token)

    # Final token should become MEGRE
    if len(tokens) == 0:
        # Safety: shouldn’t happen for valid filenames
        tokens = ["MEGRE"]
    else:
        tokens[-1] = "MEGRE"

    return "_".join(tokens)

def paired_nii_from_json(json_path):
    """
    Given a .json path, return the expected .nii.gz path with same stem in the same directory.
    """
    return json_path.with_suffix('').with_suffix('.nii.gz')

def move_and_rename(src_path, dst_path, dry_run=False):
    """
    Move/rename src_path -> dst_path. Create parent dirs of dst_path.
    """
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    if dst_path.exists():
        print(f"[WARN] Destination exists, skipping: {dst_path}", file=sys.stderr)
        return False
    print(f"[MOVE] {src_path}  ->  {dst_path}")
    if not dry_run:
        src_path.rename(dst_path)
    return True

def clean_up_dir_if_empty(dir_path, dry_run=False):
    """
    Remove directory if empty (recursively check there are no files/subdirs left).
    """
    try:
        # Only delete if empty
        if any(dir_path.iterdir()):
            return False
        print(f"[RMDIR] {dir_path}")
        if not dry_run:
            dir_path.rmdir()
        return True
    except FileNotFoundError:
        return False

def process_swi_dir(swi_dir, dry_run=False):
    """
    Process a single swi directory: find *_qsm.json files, decide part, rename/move pairs.
    After moving everything, remove swi dir if empty.
    """
    moved_any = False
    json_files = sorted(swi_dir.glob("*_qsm.json"))

    if not json_files:
        return False

    for json_path in json_files:
        # Read metadata to decide part
        try:
            with json_path.open('r') as jf:
                meta = json.load(jf)
        except Exception as e:
            print(f"[ERROR] Could not read JSON {json_path}: {e}", file=sys.stderr)
            continue

        part_kind = decide_part_from_imagetype(meta.get("ImageType"))
        if part_kind is None:
            print(f"[WARN] Could not decide part-mag/part-phase from ImageType in {json_path}, skipping.", file=sys.stderr)
            continue

        nii_path = paired_nii_from_json(json_path)
        if not nii_path.exists():
            print(f"[WARN] Paired NIfTI not found for {json_path.name} (expected {nii_path.name}), skipping.", file=sys.stderr)
            continue

        old_stem = json_path.stem  # without .json
        new_stem = transform_basename(old_stem, part_kind)

        # Destination: session anat folder
        # swi_dir = .../sub-XXXX/ses-YY/swi
        ses_dir = swi_dir.parent  # .../sub-XXXX/ses-YY
        anat_dir = ses_dir / "anat"

        new_json = anat_dir / f"{new_stem}.json"
        new_nii = anat_dir / f"{new_stem}.nii.gz"

        ok1 = move_and_rename(json_path, new_json, dry_run=dry_run)
        ok2 = move_and_rename(nii_path, new_nii, dry_run=dry_run)
        moved_any = moved_any or (ok1 and ok2)

    # If everything moved and directory is empty, remove it
    # Attempt to remove repeatedly in case intermediate files (e.g., leftover) also gone
    try:
        if not any(swi_dir.iterdir()):
            clean_up_dir_if_empty(swi_dir, dry_run=dry_run)
    except FileNotFoundError:
        pass

    return moved_any

def main():
    parser = argparse.ArgumentParser(
        description="Rename and move SWI QSM files to MEGRE in anat/, setting part-mag/part-phase from JSON ImageType."
    )
    parser.add_argument(
        "base_dir",
        nargs="?",
        default="/cbica/projects/executive_function/data/bids/EF_bids_data_DataLad",
        help="Path to EF_bids_data_DataLad"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without renaming/moving/deleting."
    )
    args = parser.parse_args()

    base = Path(args.base_dir).resolve()
    if not base.exists():
        print(f"[ERROR] Base directory does not exist: {base}", file=sys.stderr)
        sys.exit(1)

    # Walk sub-*/ses-*/swi/
    swi_dirs = sorted(base.glob("sub-*/ses-*/swi"))
    if not swi_dirs:
        print("[INFO] No swi/ directories found. Nothing to do.")
        return

    total = 0
    changed = 0
    for swi_dir in swi_dirs:
        total += 1
        print(f"[SCAN] {swi_dir}")
        if process_swi_dir(swi_dir, dry_run=args.dry_run):
            changed += 1

    print(f"[DONE] Processed {total} swi/ directories; changed {changed}.")

if __name__ == "__main__":
    main()
