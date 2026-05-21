import os
import random
from glob import glob

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd
import seaborn as sns
from nilearn.glm.first_level import make_first_level_design_matrix
from nilearn.maskers import NiftiSpheresMasker
from nilearn.maskers.nifti_spheres_masker import apply_mask_and_get_affinity
from scipy import stats

sns.set_style("whitegrid")

# Centroids of spherical ROIs in XYZ (MNI)
rois = [
    (-26, -76, 38),
    (26, -72, 42),
    (8, -56, 70),
    (34, 4, -46),
    (-18, -2, 0),
    (0, 24, -14),
    (52, -42, 46),
    (6, -68, 50),
    (32, -90, -18),
]

roi_colors = [
    "red",
    "orange",
    "gold",
    "green",
    "cyan",
    "blue",
    "purple",
    "magenta",
    "brown",
    "black",
]

# Number of runs to plot
n_runs = 10

bids_root = "/cbica/projects/executive_function/data/bids/EF_bids_data_DataLad"
in_dir = "/cbica/projects/executive_function/EF_dataset/derivatives/fmriprep_unzipped/fmriprep_func"
out_dir = "/cbica/projects/executive_function/code/task_contrast/final/results_plot_timeseries"
os.makedirs(out_dir, exist_ok=True)

preproc_files = sorted(
    glob(
        os.path.join(
            in_dir,
            "sub-*",
            "ses-*",
            "func",
            "*_task-nback_run-*_space-MNI152NLin6Asym_res-2_desc-preproc_bold.nii.gz",
        )
    )
)

if len(preproc_files) == 0:
    raise RuntimeError("No preprocessed files found.")

n_runs = min(n_runs, len(preproc_files))
selected_preproc_files = random.sample(preproc_files, n_runs)

for preproc_file in selected_preproc_files:
    print(preproc_file)

    rel_func = os.path.relpath(os.path.dirname(preproc_file), in_dir)
    preproc_base = os.path.basename(preproc_file)
    events_name = preproc_base.split("_space-")[0] + "_events.tsv"
    events_file = os.path.join(bids_root, rel_func, events_name)
    mask = preproc_file.replace("desc-preproc_bold.nii.gz", "desc-brain_mask.nii.gz")
    confounds_file = preproc_file.replace(
        "_space-MNI152NLin6Asym_res-2_desc-preproc_bold.nii.gz",
        "_desc-confounds_timeseries.tsv",
    )

    if not os.path.exists(events_file):
        print(f"\tSkipping (no events file): {events_file}")
        continue

    if not os.path.exists(mask):
        print(f"\tSkipping (no mask file): {mask}")
        continue

    if not os.path.exists(confounds_file):
        print(f"\tSkipping (no confounds file): {confounds_file}")
        continue

    events = pd.read_table(events_file)
    confounds = pd.read_table(confounds_file)

    required_cols = {"onset", "duration", "trial_type"}
    if not required_cols.issubset(events.columns):
        print(f"\tSkipping (missing required columns in events): {events_file}")
        continue

    # Rename trial_type labels before building design matrix
    events["trial_type"] = events["trial_type"].replace(
        {
            "0BACK": "zero_back",
            "2BACK": "two_back",
        }
    )
    events = events[["onset", "duration", "trial_type"]]

    # Load image to get actual number of scans
    img = nib.load(preproc_file)
    mask_img = nib.load(mask)

    t_r = 0.8
    n_scans = img.shape[-1]

    # Detect dummy scans from fMRIPrep confounds
    nss_cols = [c for c in confounds.columns if c.startswith("non_steady_state_outlier")]
    n_dummy = len(nss_cols)
    print(f"\tDetected {n_dummy} dummy scans")

    if n_dummy >= n_scans:
        print("\tSkipping run (dummy scans >= total scans)")
        continue

    # Trim frame times to exclude dummy scans
    frame_times = np.arange(n_scans) * t_r
    frame_times = frame_times[n_dummy:] - (n_dummy * t_r)

    # Shift events earlier by removed dummy-scan time
    events = events.copy()
    events["onset"] = events["onset"] - (n_dummy * t_r)

    # Drop events that end before the trimmed run starts
    events = events[events["onset"] + events["duration"] > 0].copy()

    # Clip partially overlapping events to start at 0
    events["onset"] = events["onset"].clip(lower=0)

    # Build design matrix
    print("\tConvolving task regressors")
    dm = make_first_level_design_matrix(
        frame_times,
        events,
        drift_model=None,
        hrf_model="glover",
    )

    cols = [c for c in dm.columns if c != "constant"]
    dm = dm[cols]

    dm_colors = {
        "zero_back": "blue",
        "two_back": "green",
    }

    fig, ax = plt.subplots(figsize=(10, 5))

    # Plot task regressors
    for reg_name, regressor in dm.items():
        regressor_z = stats.zscore(regressor, nan_policy="omit")
        color = dm_colors.get(reg_name, None)
        ax.plot(
            frame_times,
            regressor_z,
            alpha=0.7,
            label=reg_name,
            color=color,
            linewidth=2,
        )

    # Keep only ROIs that are non-empty for this run
    print("\tChecking ROI spheres")
    valid_rois = []
    valid_colors = []

    for roi, color in zip(rois, roi_colors):
        try:
            apply_mask_and_get_affinity(
                seeds=[roi],
                niimg=img,
                radius=3,
                allow_overlap=True,
                mask_img=mask_img,
            )
            valid_rois.append(roi)
            valid_colors.append(color)
        except ValueError:
            print(f"\tSkipping empty sphere: {roi}")

    if len(valid_rois) == 0:
        print("\tSkipping run (no valid ROIs)")
        plt.close(fig)
        continue

    # Extract ROI time series
    print("\tInitializing masker")
    masker = NiftiSpheresMasker(
        seeds=valid_rois,
        radius=3,
        mask_img=mask,
        standardize=False,
    )

    print("\tFitting masker")
    rois_timeseries = masker.fit_transform(preproc_file)

    # Trim dummy scans from ROI time series
    rois_timeseries = rois_timeseries[n_dummy:, :]

    # Plot ROI time series
    for i_roi, centroid in enumerate(valid_rois):
        roi_timeseries = rois_timeseries[:, i_roi]
        roi_timeseries_z = stats.zscore(roi_timeseries, nan_policy="omit")

        centroid_name = f"{centroid[0]}x{centroid[1]}x{centroid[2]}"
        ax.plot(
            frame_times,
            roi_timeseries_z,
            alpha=0.5,
            label=centroid_name,
            color=valid_colors[i_roi],
        )

    ax.set_xlim(0, np.max(frame_times))
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Z-scored signal")
    ax.set_title(os.path.basename(preproc_file))
    ax.legend(fontsize=8, bbox_to_anchor=(1.02, 1), loc="upper left")

    out_file = os.path.join(
        out_dir,
        os.path.basename(events_file).replace("_events.tsv", ".png"),
    )
    fig.savefig(out_file, bbox_inches="tight", dpi=150)
    plt.close(fig)

    print(f"\tSaved: {out_file}")
    print("\tDone")
