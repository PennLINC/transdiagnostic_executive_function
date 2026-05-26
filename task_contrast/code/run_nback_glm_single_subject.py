#!/usr/bin/env python
"""Run first-level GLM for n-back task within a single subject."""

import sys
import re
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm
from nilearn.glm.first_level import first_level_from_bids
from nilearn.interfaces.bids import save_glm_to_bids


# ============================================================
# GET SUBJECT FROM COMMAND LINE
# ============================================================
sub_id = sys.argv[1]
sub_labels = [sub_id]

print(f"Running first-level GLM for subject: {sub_id}")

bids_root = Path("/cbica/projects/executive_function/data/bids/EF_bids_data_DataLad")

derivatives_folder = (
    "/cbica/projects/executive_function/EF_dataset/derivatives/"
    "fmriprep_unzipped/fmriprep_func"
)
deriv_root = Path(derivatives_folder)

exclusions_file = Path(
    "/cbica/projects/executive_function/code/task_contrast/final/"
    "task_contrast_exclusions.csv"
)

exclusions = pd.read_csv(exclusions_file, dtype=str)
exclusions["participant_id"] = (
    exclusions["participant_id"].str.replace("^sub-", "", regex=True)
)
exclusions["session_id"] = (
    exclusions["session_id"].str.replace("^ses-", "", regex=True)
)

csv_excluded_sessions = set(
    zip(exclusions["participant_id"], exclusions["session_id"])
)

task_label = "nback"
space_label = "MNI152NLin6Asym"


# ============================================================
# MINIMAL SESSION CHECKS
# ============================================================
def get_entity(fname, entity):
    match = re.search(rf"(?:^|_){entity}-([^_]+)", fname)
    return match.group(1) if match else None


bold_pattern = (
    f"sub-{sub_id}/ses-*/func/"
    f"sub-{sub_id}_ses-*_task-{task_label}*"
    f"_space-{space_label}_res-2_desc-preproc_bold.nii.gz"
)
bold_files = sorted(deriv_root.glob(bold_pattern))

usable_sessions = set()
missing_events_sessions = []
all_na_response_sessions = []
csv_excluded_sessions_this_sub = []

for bold_file in bold_files:
    fname = bold_file.name
    ses = get_entity(fname, "ses")
    run = get_entity(fname, "run")
    acq = get_entity(fname, "acq")

    if (sub_id, ses) in csv_excluded_sessions:
        csv_excluded_sessions_this_sub.append(f"sub-{sub_id}_ses-{ses}")
        continue

    events_pattern = (
        f"sub-{sub_id}/ses-{ses}/func/"
        f"sub-{sub_id}_ses-{ses}_task-{task_label}"
    )
    if acq is not None:
        events_pattern += f"_acq-{acq}"
    if run is not None:
        events_pattern += f"_run-{run}"
    events_pattern += "_events.tsv"

    events_files = sorted(bids_root.glob(events_pattern))

    if len(events_files) == 0:
        missing_events_sessions.append(f"sub-{sub_id}_ses-{ses}_run-{run}")
        continue

    events = pd.read_csv(events_files[0], sep="\t")
    response_time = pd.to_numeric(events["response_time"], errors="coerce")

    if response_time.isna().all():
        all_na_response_sessions.append(f"sub-{sub_id}_ses-{ses}_run-{run}")
        continue

    usable_sessions.add(ses)

usable_sessions = sorted(usable_sessions)

print("\nSessions excluded because response_time was all n/a:")
if all_na_response_sessions:
    for x in all_na_response_sessions:
        print(f"  {x}")
else:
    print("  None")

print("\nSessions with missing events.tsv:")
if missing_events_sessions:
    for x in missing_events_sessions:
        print(f"  {x}")
else:
    print("  None")

print("\nSessions excluded based on task_contrast_exclusions.csv:")
if csv_excluded_sessions_this_sub:
    for x in sorted(set(csv_excluded_sessions_this_sub)):
        print(f"  {x}")
else:
    print("  None")

if missing_events_sessions and usable_sessions:
    print(
        f"\n[PROCEEDING] sub-{sub_id}: one or more sessions had missing events.tsv, "
        f"but usable sessions remain: {usable_sessions}"
    )

if len(usable_sessions) == 0:
    print("\nEntirely excluded subject:")
    print(f"  sub-{sub_id}: no usable sessions remain")
    print("\nSkipping first-level GLM.\n")
    sys.exit(0)

print("\nEntirely excluded subject:")
print("  None")
print(f"\nUsable sessions for sub-{sub_id}: {usable_sessions}\n")


# ============================================================
# FIND FMRIPREP BRAIN MASK FOR THIS SUBJECT
# ============================================================
mask_pattern = (
    f"sub-{sub_id}/ses-*/func/"
    f"sub-{sub_id}_ses-*_task-{task_label}*"
    f"_space-{space_label}_res-2_desc-brain_mask.nii.gz"
)
mask_candidates = sorted(deriv_root.glob(mask_pattern))

mask_img = None
if len(mask_candidates) == 0:
    print(
        f"[WARNING] No fMRIPrep brain mask found for sub-{sub_id} with pattern:\n"
        f"  {mask_pattern}\n"
        "Falling back to Nilearn's automatic mask.\n"
    )
else:
    mask_img = str(mask_candidates[0])
    print(f"Using fMRIPrep brain mask for sub-{sub_id}:\n  {mask_img}\n")


# ============================================================
# BUILD FIRST-LEVEL MODEL FROM BIDS
# ============================================================
MODEL_TYPES = ["rtdur", "nortdur"]
for model_type in MODEL_TYPES:
    out_dir = Path(
        f"/cbica/projects/executive_function/code/task_contrast/final/"
        f"results_final_3_edited/first-level/nback-{model_type}"
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    model = None
    run_imgs = []
    events_list = []
    confounds_list = []

    for ses in usable_sessions:
        (
            models,
            models_run_imgs,
            models_events,
            models_confounds,
        ) = first_level_from_bids(
            dataset_path=bids_root,
            task_label=task_label,
            space_label=space_label,
            sub_labels=sub_labels,
            derivatives_folder=derivatives_folder,
            img_filters=[("desc", "preproc"), ("ses", ses)],
            smoothing_fwhm=5.0,
            n_jobs=4,
            verbose=1,
            drift_model=None,
            confounds_strategy=("motion", "high_pass", "compcor"),
            confounds_motion="basic",
            confounds_compcor="anat_combined",
            confounds_n_compcor=5,
            mask_img=mask_img,
        )

        if model is None:
            model = models[0]

        this_run_imgs = models_run_imgs[0]
        this_events = models_events[0]
        this_confounds = models_confounds[0]

        if not isinstance(this_run_imgs, list):
            this_run_imgs = [this_run_imgs]
        if isinstance(this_events, pd.DataFrame):
            this_events = [this_events]
        if isinstance(this_confounds, pd.DataFrame):
            this_confounds = [this_confounds]

        run_imgs.extend(this_run_imgs)
        events_list.extend(this_events)
        confounds_list.extend(this_confounds)

    updated_events_list = []
    for events in events_list:
        events = events.copy()

        # ---- drop INSTRUCTION trials ----
        events = events.loc[events["trial_type"] != "INSTRUCTION"].copy()

        if "trial_type" in events.columns:
            events["trial_type"] = events["trial_type"].replace(
                {
                    "0BACK": "zero_back",
                    "2BACK": "two_back",
                }
            )

        if model_type == "rtdur":
            response_time = pd.to_numeric(events["response_time"], errors="coerce")
            response_events = events.loc[~response_time.isna()].copy()
            response_events.loc[:, "duration"] = response_time.loc[response_events.index]
            response_events.loc[:, "trial_type"] = "RTDur"
            events = pd.concat((events, response_events))
            events = events.sort_values(by="onset")

        updated_events_list.append(events)

    print(f"Number of runs for subject {sub_id}: {len(run_imgs)}")
    print("Confounds entries for each run:")
    for i, c in enumerate(confounds_list):
        print(f"  Run {i}: {c}")

    model.minimize_memory = False

    print(f"\nFitting {model_type} GLM for subject {sub_id}...")
    model = model.fit(
        run_imgs,
        events=updated_events_list,
        confounds=confounds_list,
    )

    design_matrix = model.design_matrices_[0]
    print("\nDesign matrix columns:")
    print(design_matrix.columns)
    print(f"\nTotal # regressors in design matrix: {design_matrix.shape[1]}")

    save_glm_to_bids(
        model,
        contrasts=["two_back - zero_back", "two_back", "zero_back"],
        contrast_types={
            "two_back - zero_back": "t",
            "two_back": "t",
            "zero_back": "t",
        },
        out_dir=out_dir,
        height_control=None,
        threshold=norm.isf(0.001),
        cluster_threshold=10,
        two_sided=True,
        bg_img=(
            "/cbica/projects/executive_function/templateflow/"
            "tpl-MNI152NLin6Asym/tpl-MNI152NLin6Asym_res-02_T1w.nii.gz"
        ),
    )

print("\nDone.\n")
