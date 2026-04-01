#!/usr/bin/env python3
"""
Compute group mean & SD for fsLR-91k ALFF and ReHo (XCP-D dscalar),
splitting results by task label (e.g., rest, nback).

Outputs (examples):
  group-alff_task-rest_space-fsLR_den-91k_stat-mean.dscalar.nii
  group-alff_task-rest_space-fsLR_den-91k_stat-sd.dscalar.nii
  group-reho_task-nback_space-fsLR_den-91k_stat-mean.dscalar.nii
  group-reho_task-nback_space-fsLR_den-91k_stat-sd.dscalar.nii

Dependencies:
  - nibabel >= 5 (CIFTI support)
  - numpy, pandas

Notes:
  - Exclusion CSV should contain a column with strings like "sub-12345_ses-1"
    that appear in the filenames you want to exclude.
  - This script assumes each input dscalar has a single map (usual for ALFF/ReHo).
"""

import os
import re
from glob import glob
from collections import defaultdict

import numpy as np
import pandas as pd
import nibabel as nb


# --------------------------- Config (edit as needed) ---------------------------

IN_DIR = "/cbica/projects/executive_function/EF_dataset/derivatives/xcpd_unzipped/xcpd"
OUT_DIR = "/cbica/projects/executive_function/EF_dataset_figures/figures/xcpd_group_maps"
EXCLUDED_CSV = "/cbica/projects/executive_function/EF_dataset_figures/processing_scripts/excluded_scans_func.csv"  # or None

# File patterns for ALFF/ReHo in fsLR-91k dscalar space
PATTERNS = {
    "ALFF": ["sub-*/ses-*/func/*_space-fsLR_den-91k_stat-alff_boldmap.dscalar.nii"],
    "ReHo": ["sub-*/ses-*/func/*_space-fsLR_den-91k_stat-reho_boldmap.dscalar.nii"],
}

# If True, will print first few included files per bucket
VERBOSE_LIST = True
VERBOSE_LIST_N = 5

# ------------------------------------------------------------------------------


def find_exclusion_column(df: pd.DataFrame) -> str:
    """Heuristically find a column holding the scan identifiers to exclude."""
    # Prefer columns named like 'excluded_scans', 'excluded', 'scan', 'scans'
    candidates = [c for c in df.columns if any(k in c.lower() for k in ("excluded", "scan", "scans", "drop", "remove"))]
    if candidates:
        return candidates[0]
    # Fallback to the first column
    return df.columns[0]


def list_cifti(patterns, in_dir, excluded_csv=None):
    """Return sorted list of files matching patterns, minus any exclusions."""
    files = []
    for pat in patterns:
        files.extend(glob(os.path.join(in_dir, pat), recursive=True))
    files = sorted(files)

    if excluded_csv and os.path.exists(excluded_csv):
        excl_df = pd.read_csv(excluded_csv)
        col = find_exclusion_column(excl_df)
        excluded = set(excl_df[col].astype(str).str.strip())
        files = [f for f in files if not any(x in f for x in excluded)]

    return files


def running_mean_std(n, mean, M2, x):
    """Welford update for a single observation vector x (1D: grayordinates)."""
    n += 1
    delta = x - mean
    mean = mean + delta / n
    M2 = M2 + delta * (x - mean)
    return n, mean, M2


def load_single_map_vector(dscalar_path):
    """Load a dscalar and return a 1D vector of grayordinates."""
    img = nb.load(dscalar_path)
    data = np.asanyarray(img.get_fdata()).squeeze()
    # Common shapes: (n_maps, n_gray) with n_maps==1 OR (n_gray,)
    if data.ndim == 2:
        if 1 in data.shape:
            data = data.reshape(-1)  # flatten the single-map
        else:
            raise ValueError(f"Unexpected dscalar with >1 maps: {dscalar_path} has shape {data.shape}")
    return img, data


def compute_group_stats_dscalar(file_list):
    """
    Return (mean_vec, sd_vec, template_img) across CIFTI dscalar files.
    Uses streaming (Welford) to save memory.
    """
    if len(file_list) == 0:
        raise ValueError("No files found.")

    # Initialize with first file
    tmpl_img, first_vec = load_single_map_vector(file_list[0])
    n_gray = first_vec.size
    n = 0
    mean = np.zeros(n_gray, dtype=np.float64)
    M2 = np.zeros(n_gray, dtype=np.float64)

    for f in file_list:
        _, vec = load_single_map_vector(f)
        if vec.size != n_gray:
            raise ValueError(f"Grayordinate size mismatch: {f} has {vec.size}, expected {n_gray}")
        n, mean, M2 = running_mean_std(n, mean, M2, vec)

    var = M2 / (n - 1) if n > 1 else np.zeros_like(mean)
    sd = np.sqrt(var, dtype=np.float64)
    return mean, sd, tmpl_img


def save_dscalar(vector, template_img, out_path, map_name="stat"):
    """
    Save a 1D vector as a single-map dscalar using the axes from template_img.
    Tries to set a friendly scalar map name where possible.
    """
    data = np.atleast_2d(vector.astype(np.float32))  # (1, n_gray)

    # Rebuild header axes to ensure axis-0 has a single map (named) and axis-1 from template
    try:
        ax1 = template_img.header.get_axis(1)  # Grayordinate axis
        # Create a scalar axis with the given map_name
        scalar_axis = nb.cifti2.ScalarAxis([map_name])
        header = nb.cifti2.Cifti2Header.from_axes((scalar_axis, ax1))
        new_img = nb.Cifti2Image(data, header=header, nifti_header=template_img.nifti_header)
    except Exception:
        # Fallback: reuse template header directly (works if it already has a single map)
        new_img = nb.Cifti2Image(data, header=template_img.header, nifti_header=template_img.nifti_header)

    nb.save(new_img, out_path)
    return out_path


def bucket_by_task(file_list):
    """
    Bucket files by task label found in filename: ... task-<label> ...
    Returns dict: task -> [files...]; unknown if no task tag.
    """
    buckets = defaultdict(list)
    for f in file_list:
        m = re.search(r"task-([a-zA-Z0-9]+)", os.path.basename(f))
        task = m.group(1).lower() if m else "unknown"
        buckets[task].append(f)
    return buckets


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    for metric, pats in PATTERNS.items():
        all_files = list_cifti(pats, IN_DIR, excluded_csv=EXCLUDED_CSV)
        if len(all_files) == 0:
            print(f"[{metric}] No files found. Patterns: {pats}")
            continue

        buckets = bucket_by_task(all_files)
        for task, files in sorted(buckets.items()):
            if len(files) < 2:
                print(f"[{metric} | task={task}] Only {len(files)} file(s); skipping group stats.")
                if VERBOSE_LIST and len(files) > 0:
                    for f in files[:VERBOSE_LIST_N]:
                        print(f"  - {f}")
                continue

            print(f"[{metric} | task={task}] {len(files)} maps")
            if VERBOSE_LIST:
                for f in files[:VERBOSE_LIST_N]:
                    print(f"  - {f}")
                if len(files) > VERBOSE_LIST_N:
                    print(f"  ... (+{len(files) - VERBOSE_LIST_N} more)")

            mean_vec, sd_vec, tmpl = compute_group_stats_dscalar(files)

            mean_out = os.path.join(
                OUT_DIR,
                f"group-{metric.lower()}_task-{task}_space-fsLR_den-91k_stat-mean.dscalar.nii",
            )
            sd_out = os.path.join(
                OUT_DIR,
                f"group-{metric.lower()}_task-{task}_space-fsLR_den-91k_stat-sd.dscalar.nii",
            )

            save_dscalar(mean_vec, tmpl, mean_out, map_name=f"{metric} mean ({task})")
            save_dscalar(sd_vec, tmpl, sd_out, map_name=f"{metric} sd ({task})")

            print(f"Saved:\n  {mean_out}\n  {sd_out}")

    print("Done.")


if __name__ == "__main__":
    main()

