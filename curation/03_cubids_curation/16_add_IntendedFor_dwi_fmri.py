import os
import json
import re
from typing import Dict, List, Optional, Tuple

"""
Add IntendedFor to fmap EPI JSONs, matching to dwi/func targets by:
- subject + session (within same ses-* directory)
- run-XX
- acq-dwi* vs acq-fmri* in fmap filename

IntendedFor paths are written relative to the subject directory (sub-XXXX).
"""

BASE_DIR = "/cbica/projects/executive_function/data/bids/EF_bids_data_DataLad"

# Safety options
DRY_RUN = False          # True: don't write, just print what would happen
MAKE_BACKUP = False       # True: save original JSON as *.bak before overwriting


BIDS_KV_RE = re.compile(r"(?P<key>[a-zA-Z0-9]+)-(?P<val>[^_]+)")


def parse_bids_entities(fname: str) -> Dict[str, str]:
    """
    Parse BIDS-like entities from a filename, e.g.
      sub-23676_ses-1_acq-dwiVARIANTObliquity_dir-AP_run-01_epi.json
    Returns dict like {"sub":"23676","ses":"1","acq":"dwiVARIANTObliquity","run":"01","dir":"AP"}
    """
    entities: Dict[str, str] = {}
    # drop extensions
    stem = fname
    for ext in [".nii.gz", ".nii", ".json", ".tsv", ".bval", ".bvec"]:
        if stem.endswith(ext):
            stem = stem[: -len(ext)]
            break

    parts = stem.split("_")
    for p in parts:
        m = BIDS_KV_RE.match(p)
        if m:
            entities[m.group("key")] = m.group("val")
    return entities


def get_subject_dir_from_ses(ses_dir: str) -> str:
    """
    ses_dir = .../sub-XXXX/ses-Y
    returns .../sub-XXXX
    """
    return os.path.dirname(ses_dir)


def relpath_from_subject(subject_dir: str, abs_path: str) -> str:
    return os.path.relpath(abs_path, subject_dir)


def load_json(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def save_json(path: str, data: dict) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def index_targets_in_session(ses_dir: str) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    """
    Return:
      dwi_targets_by_run: run -> list of absolute paths to *_dwi.nii.gz
      fmri_targets_by_run: run -> list of absolute paths to *_bold.nii.gz
    """
    dwi_by_run: Dict[str, List[str]] = {}
    fmri_by_run: Dict[str, List[str]] = {}

    dwi_dir = os.path.join(ses_dir, "dwi")
    func_dir = os.path.join(ses_dir, "func")

    if os.path.isdir(dwi_dir):
        for fn in os.listdir(dwi_dir):
            if fn.endswith("_dwi.nii.gz"):
                ent = parse_bids_entities(fn)
                run = ent.get("run")
                if run:
                    dwi_by_run.setdefault(run, []).append(os.path.join(dwi_dir, fn))

    if os.path.isdir(func_dir):
        for fn in os.listdir(func_dir):
            if fn.endswith("_bold.nii.gz"):
                ent = parse_bids_entities(fn)
                run = ent.get("run")
                if run:
                    fmri_by_run.setdefault(run, []).append(os.path.join(func_dir, fn))

    return dwi_by_run, fmri_by_run


def filter_by_acq_tail(paths: List[str], acq_tail: str) -> List[str]:
    """
    If fmap has acq like 'dwiVARIANTObliquity', tail = 'VARIANTObliquity'.
    Prefer targets whose acq contains tail (e.g. acq-VARIANTObliquity).
    If none match, return original list.
    """
    if not acq_tail:
        return paths

    matched = []
    for p in paths:
        ent = parse_bids_entities(os.path.basename(p))
        acq = ent.get("acq", "")
        if acq_tail in acq:
            matched.append(p)

    return matched if matched else paths


def update_fmap_intendedfor(ses_dir: str) -> None:
    fmap_dir = os.path.join(ses_dir, "fmap")
    if not os.path.isdir(fmap_dir):
        return

    subject_dir = get_subject_dir_from_ses(ses_dir)
    dwi_by_run, fmri_by_run = index_targets_in_session(ses_dir)

    for fn in os.listdir(fmap_dir):
        if not fn.endswith("_epi.json"):
            continue

        ent = parse_bids_entities(fn)
        run = ent.get("run")
        acq = ent.get("acq", "")

        if not run:
            print(f"[SKIP] No run entity in {os.path.join(fmap_dir, fn)}")
            continue

        # Determine whether this fmap is for dwi or fmri from the *prefix* of acq
        target_kind: Optional[str] = None
        acq_tail = ""

        if acq.startswith("dwi"):
            target_kind = "dwi"
            acq_tail = acq[len("dwi"):]  # e.g. 'VARIANTObliquity' or ''
        elif acq.startswith("fmri"):
            target_kind = "fmri"
            acq_tail = acq[len("fmri"):]  # e.g. 'VARIANTObliquity' or ''
        else:
            print(f"[SKIP] acq does not start with dwi/fmri in {fn} (acq={acq})")
            continue

        if target_kind == "dwi":
            candidates = dwi_by_run.get(run, [])
            candidates = filter_by_acq_tail(candidates, acq_tail)
        else:
            candidates = fmri_by_run.get(run, [])
            candidates = filter_by_acq_tail(candidates, acq_tail)

        if not candidates:
            print(f"[NO MATCH] {fn} (run-{run}, acq={acq}) -> no {target_kind} targets found")
            continue

        intended = [relpath_from_subject(subject_dir, p) for p in sorted(candidates)]
        intended_value = intended[0] if len(intended) == 1 else intended

        json_path = os.path.join(fmap_dir, fn)
        data = load_json(json_path)

        # Only report if changed
        prev = data.get("IntendedFor", None)
        data["IntendedFor"] = intended_value

        if prev == intended_value:
            print(f"[OK] {fn} already has correct IntendedFor")
            continue

        print(f"[UPDATE] {fn}")
        print(f"         IntendedFor = {intended_value}")

        if DRY_RUN:
            continue

        if MAKE_BACKUP:
            bak_path = json_path + ".bak"
            if not os.path.exists(bak_path):
                with open(bak_path, "w") as f:
                    json.dump(prev if prev is not None else data, f, indent=4)

        save_json(json_path, data)


def main():
    # Find all session directories: .../sub-*/ses-*
    for root, dirs, files in os.walk(BASE_DIR):
        base = os.path.basename(root)
        if base.startswith("ses-") and os.path.basename(os.path.dirname(root)).startswith("sub-"):
            update_fmap_intendedfor(root)


if __name__ == "__main__":
    main()

