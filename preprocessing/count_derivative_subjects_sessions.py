#!/usr/bin/env python3
"""
Count subjects and sessions in EF derivatives (aslprep, fmriprep, qsiprep, qsirecon, xcpd).

Per derivative directory, this script prints:
  - # of subjects (unique sub-*/ directories directly under the pipeline root) and the subject list
  - # of sessions (unique ses-* directories under those subjects) and the sub/ses list

It uses the nested roots you provided (examples):
  - aslprep_unzipped/aslprep
  - fmriprep_anat_unzipped/fmriprep_anat
  - fmriprep_unzipped/fmriprep_func  (also tolerates 'fmriprep_unnzipped')
  - qsiprep_unzipped/qsiprep
  - qsirecon_unzipped/qsirecon/derivatives/qsirecon-DSIStudio
  - xcpd_unzipped/xcpd

Usage:
  python count_derivative_subjects_sessions.py /path/to/EF_dataset/derivatives

Notes:
- Only counts directories named 'sub-*' at the pipeline root, and 'ses-*' under each subject.
- Ignores non-BIDS folders ('figures', 'log', '*.html', etc.).
- Output is printed; no files are created.
"""

import argparse
from pathlib import Path
from typing import List, Tuple


def natural_key(s: str) -> List:
    import re
    parts = re.split(r'(\d+)', s)
    return [int(p) if p.isdigit() else p for p in parts]


def pick_existing_inner(base: Path, candidates: List[str]) -> Path:
    """
    Given a base path and a list of relative candidate inner roots, return the first that exists.
    If none exists, return a non-existing path (base / candidates[0]) so the caller can report.
    """
    for rel in candidates:
        p = base / rel
        if p.exists() and p.is_dir():
            return p
    return base / candidates[0]


def find_subjects(pipeline_root: Path) -> List[Path]:
    subs = [d for d in pipeline_root.iterdir() if d.is_dir() and d.name.startswith("sub-")]
    subs.sort(key=lambda p: natural_key(p.name))
    return subs


def find_sessions(sub_dir: Path) -> List[Path]:
    sess = [d for d in sub_dir.iterdir() if d.is_dir() and d.name.startswith("ses-")]
    sess.sort(key=lambda p: natural_key(p.name))
    return sess


def summarize_pipeline(print_name: str, inner_root: Path) -> None:
    if not inner_root.exists() or not inner_root.is_dir():
        print(f"\n[{print_name}]")
        print(f"  Expected inner root does not exist: {inner_root}")
        return

    subs = find_subjects(inner_root)
    sub_names = [s.name for s in subs]

    # sessions as flattened list of "sub-xxx/ses-y"
    ses_pairs: List[Tuple[str, str]] = []
    for s in subs:
        for ses in find_sessions(s):
            ses_pairs.append((s.name, ses.name))

    ses_pairs.sort(key=lambda t: (natural_key(t[0]), natural_key(t[1])))

    # ---- print summary ----
    print(f"\n[{print_name}]")
    print(f"Pipeline root: {inner_root}")

    print(f"  # of subjects: {len(subs)}")
    if subs:
        # pretty-wrap subjects to ~100 chars per line
        line = "  Subjects: "
        first_in_line = True
        for i, name in enumerate(sub_names):
            token = ("" if first_in_line else ", ") + name
            if len(line) + len(token) > 100:
                print(line)
                line = "            " + name
                first_in_line = False
            else:
                line += token
                first_in_line = False
        if line.strip():
            print(line)
    else:
        print("  Subjects: None")

    print(f"  # of sessions: {len(ses_pairs)}")
    if ses_pairs:
        print("  Sessions (sub/ses):")
        for sub, ses in ses_pairs:
            print(f"    {sub}/{ses}")
    else:
        print("  Sessions: None")


def main():
    parser = argparse.ArgumentParser(description="Count sub-/ses- across EF derivatives.")
    parser.add_argument("derivatives_root", type=Path, help="Path to EF_dataset/derivatives")
    args = parser.parse_args()

    base = args.derivatives_root
    if not base.exists() or not base.is_dir():
        raise SystemExit(f"Error: Not a directory: {base}")

    # Map of outer dir -> candidate inner roots (relative to outer dir)
    # We tolerate the 'fmriprep_unnzipped' misspelling by checking both outers below.
    pipelines = [
        # (print_name, outer_dir_name, [inner_root_candidates...])
        ("aslprep_unzipped", "aslprep_unzipped", ["aslprep"]),
        ("fmriprep_anat_unzipped", "fmriprep_anat_unzipped", ["fmriprep_anat"]),
        ("fmriprep_unzipped", "fmriprep_unzipped", ["fmriprep_func", "fmriprep"]),
        ("fmriprep_unnzipped", "fmriprep_unnzipped", ["fmriprep_func", "fmriprep"]),  # typo-tolerant
        ("qsiprep_unzipped", "qsiprep_unzipped", ["qsiprep"]),
        ("qsirecon_unzipped", "qsirecon_unzipped", ["qsirecon/derivatives/qsirecon-DSIStudio"]),
        ("xcpd_unzipped", "xcpd_unzipped", ["xcpd_unzipped/xcpd"]),
    ]

    seen_fmriprep = False  # avoid double-printing if both spellings exist
    for print_name, outer_name, inner_candidates in pipelines:
        outer = base / outer_name
        if not outer.exists() or not outer.is_dir():
            # Quietly skip missing outer dirs
            continue

        if "fmriprep_unzipped" in (print_name, outer_name):
            seen_fmriprep = True
        if "fmriprep_unnzipped" in (print_name, outer_name) and seen_fmriprep:
            # if we already printed the correctly spelled one, skip the typo one
            continue

        inner_root = pick_existing_inner(outer, inner_candidates)
        summarize_pipeline(print_name, inner_root)


if __name__ == "__main__":
    main()

