import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

from nilearn.glm.first_level import first_level_from_bids
from nilearn.interfaces.bids import save_glm_to_bids


# ============================================================
# GET SUBJECT FROM COMMAND LINE
# ============================================================

sub_id = sys.argv[1]  # subject passed by SLURM array / CLI
sub_labels = [sub_id]  # nilearn expects a list

print(f"Running first-level GLM for subject: {sub_id}")

# ---------- CONFIG ----------

# BIDS root
bids_root = Path("/cbica/projects/executive_function/data/bids/EF_bids_data_DataLad")

# fMRIPrep derivatives containing preprocessed func + confounds
derivatives_folder = (
    "/cbica/projects/executive_function/EF_dataset/derivatives/"
    "fmriprep_unzipped/fmriprep_func"
)
deriv_root = Path(derivatives_folder)

# Task and space
task_label = "nback"
space_label = "MNI152NLin6Asym"

# Output directory for maps + reports
out_dir = Path(
    "/cbica/projects/executive_function/EF_dataset/derivatives/nilearn_firstlevel_nback"
)
out_dir.mkdir(parents=True, exist_ok=True)

# Smoothing to apply in Nilearn
smoothing_fwhm = 5.0

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
    img_filters=[("desc", "preproc")],
    smoothing_fwhm=smoothing_fwhm,
    n_jobs=4,
    verbose=1,
    drift_model=None,
    confounds_strategy=("motion", "high_pass", "compcor"),
    confounds_motion="basic",
    confounds_compcor="anat_combined",
    confounds_n_compcor=5,
    mask_img=mask_img,
)

# Single subject
model = models[0]
run_imgs = models_run_imgs[0]
events_list = models_events[0]
confounds_list = models_confounds[0]

# Implement Jeanette Mumford's ConsDurRTDur model
# and rename trial types:
#   0BACK -> zero_back
#   2BACK -> two_back
cons_dur_rt_dur_events_list = []
for events in events_list:
    events = events.copy()

    if "trial_type" in events.columns:
        events["trial_type"] = events["trial_type"].replace(
            {
                "0BACK": "zero_back",
                "2BACK": "two_back",
            }
        )

    response_events = events.loc[~np.isnan(events["response_time"])].copy()
    response_events.loc[:, "duration"] = response_events.loc[:, "response_time"]
    response_events.loc[:, "trial_type"] = "RTDur"

    events = pd.concat((events, response_events))
    events = events.sort_values(by="onset")
    cons_dur_rt_dur_events_list.append(events)

print(f"Number of runs for subject {sub_id}: {len(run_imgs)}")
print("Confounds entries for each run:")
for i, c in enumerate(confounds_list):
    print(f"  Run {i}: {c}")

# ---------- FIT MODEL ----------

model.minimize_memory = False

print(f"\nFitting GLM for subject {sub_id}...")
model = model.fit(
    run_imgs,
    events=cons_dur_rt_dur_events_list,
    confounds=confounds_list,
)

# Inspect design matrix
design_matrix = model.design_matrices_[0]
print("\nDesign matrix columns:")
print(design_matrix.columns)
print(f"\nTotal # regressors in design matrix: {design_matrix.shape[1]}")

output_dir = Path.cwd() / "results" / "plot_bids_features"
output_dir.mkdir(exist_ok=True, parents=True)

# ============================================================
# SAVE SEPARATE 2-BACK AND 0-BACK CONTRASTS  (EDITED)
# ============================================================

contrasts = {
    "twoBack": "two_back",     # 2-back vs implicit baseline
    "zeroBack": "zero_back",   # 0-back vs implicit baseline
}

contrast_types = {
    "twoBack": "t",
    "zeroBack": "t",
}

save_glm_to_bids(
    model,
    contrasts=contrasts,
    contrast_types=contrast_types,
    out_dir=output_dir / "derivatives" / "nilearn_glm_SEPARATE",  # <-- changed
    threshold=norm.isf(0.001),
    cluster_threshold=10,
    bg_img=(
        "/cbica/projects/executive_function/templateflow/"
        "tpl-MNI152NLin6Asym/tpl-MNI152NLin6Asym_res-02_T1w.nii.gz"
    ),
)

print("\nDone.\n")

