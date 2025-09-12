#!/usr/bin/env python3
"""
Add `"Units": "arbitrary"` to MEGRE phase JSON sidecars in a BIDS tree.

Targets files matching:
  sub-*_ses-*_echo-*_part-phase_MEGRE.json
under: sub-*/ses-*/anat/

Usage:
  python add_megre_phase_units.py /cbica/projects/executive_function/data/bids/EF_bids_data_DataLad/ --apply

By default this runs in dry-run mode and only prints what it *would* change.
Use --apply to write changes.
"""

import argparse
import json
import sys
from pathlib import Path
import fnmatch

PATTERN = "sub-*_ses-*_echo-*_part-phase_MEGRE.json"

def find_targets(root: Path):
    # Walk only sub-*/ses-*/anat/ directories for speed/safety
    for sub in root.glob("sub-*"):
        ses_dirs = (sub / "ses-1",) if (sub / "ses-1").exists() else sub.glob("ses-*")
        for ses in ses_dirs:
            anat = ses / "anat"
            if not anat.is_dir():
                continue
            for p in anat.iterdir():
                if p.is_file() and fnmatch.fnmatch(p.name, PATTERN):
                    yield p

def process_file(p: Path, apply: bool) -> str:
    try:
        txt = p.read_text(encoding="utf-8")
        data = json.loads(txt)
    except Exception as e:
        return f"[SKIP:invalid-json] {p} ({e})"

    if "Units" in data:
        # Already has Units; leave as-is
        return f"[OK:exists]          {p} (Units={data.get('Units')!r})"

    # Add Units
    data["Units"] = "arbitrary"

    if apply:
        try:
            # Write pretty JSON with stable ordering
            p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            return f"[WROTE]              {p} (+ Units='arbitrary')"
        except Exception as e:
            return f"[ERROR:write]        {p} ({e})"
    else:
        return f"[DRY-RUN:would add]   {p} (+ Units='arbitrary')"

def main():
    ap = argparse.ArgumentParser(description="Add Units to MEGRE phase JSON sidecars.")
    ap.add_argument("root", type=Path, help="Path to BIDS root (e.g., /cbica/.../EF_bids_data_DataLad/)")
    ap.add_argument("--apply", action="store_true", help="Actually write changes (default is dry-run).")
    args = ap.parse_args()

    root = args.root
    if not root.exists():
        print(f"Root path does not exist: {root}", file=sys.stderr)
        sys.exit(1)

    targets = list(find_targets(root))
    if not targets:
        print("No matching MEGRE phase JSON files found.")
        return

    print(f"Found {len(targets)} candidate file(s). Mode: {'APPLY' if args.apply else 'DRY-RUN'}")
    changed = 0
    existed = 0
    skipped = 0

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
