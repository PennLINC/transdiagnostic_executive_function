#!/usr/bin/env python3
"""
This script adds `"Units": "arbitrary"` to MEGRE phase JSON sidecars.

Targets files matching:
  sub-*/ses-*/anat/sub-*_ses-*_echo-*_part-phase_MEGRE.json

Usage:
  python add_megre_phase_units.py /cbica/projects/executive_function/data/bids/EF_bids_data_DataLad/ --apply

By default this runs in dry-run mode and only prints what it *would* change.
Use --apply to write changes.
"""

import argparse
import json
from pathlib import Path

PATTERN = "sub-*/ses-*/anat/sub-*_ses-*_echo-*_part-phase_MEGRE.json"

def find_targets(root: Path):
    # Scan all sessions under all subjects, but only in anat/
    yield from root.glob(PATTERN)

def process_file(p: Path, apply: bool) -> str:
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        return f"[SKIP:invalid-json] {p} ({e})"

    if "Units" in data:
        return f"[OK:exists]          {p} (Units={data.get('Units')!r})"

    # Append Units at the end (Py3.7+ preserves insertion order)
    data["Units"] = "arbitrary"

    if apply:
        try:
            # Using indent=4 to match the style in your example; trailing newline included
            p.write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
            return f"[WROTE]              {p} (+ Units='arbitrary')"
        except Exception as e:
            return f"[ERROR:write]        {p} ({e})"
    else:
        return f"[DRY-RUN:would add]   {p} (+ Units='arbitrary')"

def main():
    ap = argparse.ArgumentParser(description="Add Units to MEGRE phase JSON sidecars.")
    ap.add_argument("root", type=Path, help="Path to BIDS root")
    ap.add_argument("--apply", action="store_true", help="Actually write changes (default: dry-run).")
    args = ap.parse_args()

    targets = list(find_targets(args.root))
    print(f"Found {len(targets)} candidate file(s). Mode: {'APPLY' if args.apply else 'DRY-RUN'}")

    changed = existed = skipped = 0
    for p in targets:
        msg = process_file(p, args.apply)
        print(msg)
        if msg.startswith("[WROTE]") or msg.startswith("[DRY-RUN:would add]"):
            changed += 1
        elif msg.startswith("[OK:exists]"):
            existed += 1
        else:
            skipped += 1

    print("\nSummary:")
    print(f"  Would add/Added Units: {changed}")
    print(f"  Already had Units:     {existed}")
    print(f"  Skipped (errors):      {skipped}")

if __name__ == "__main__":
    main()

