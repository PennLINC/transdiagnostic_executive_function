#!/usr/bin/env python

from pathlib import Path
import pandas as pd
import numpy as np
from scipy.stats import norm

from nilearn.glm.second_level import SecondLevelModel
from nilearn.interfaces.bids import save_glm_to_bids
from nilearn.image import load_img


# ----------------------------------------------------------
# CONFIG
# ----------------------------------------------------------

task_label = "nback"
space_label = "MNI152NLin6Asym"

# Match filenames exactly
contrast_labels = {
    "twoback": "group_twoback",
    "zeroback": "group_zeroback",
}

firstlevel_dir = Path(
    "/cbica/projects/executive_function/code/task_contrast/"
    "results/plot_bids_features/derivatives/nilearn_glm_SEPARATE"
)

# single output root
group_out_root = firstlevel_dir / "group_level_bids_SEPARATE"
group_out_root.mkdir(exist_ok=True, parents=True)


# ----------------------------------------------------------
# TEMPLATEFLOW MASK + BG
# ----------------------------------------------------------

group_mask_img = load_img(
    "/cbica/projects/executive_function/.cache/templateflow/"
    "tpl-MNI152NLin6Asym/tpl-MNI152NLin6Asym_res-02_desc-brain_mask.nii.gz"
)

bg_img = load_img(
    "/cbica/projects/executive_function/.cache/templateflow/"
    "tpl-MNI152NLin6Asym/tpl-MNI152NLin6Asym_res-02_desc-brain_T1w.nii.gz"
)


# ----------------------------------------------------------
# RUN GROUP MODELS
# ----------------------------------------------------------

for contrast_label, group_contrast_name in contrast_labels.items():

    print("\n====================================================")
    print(f"Running group model for contrast: {contrast_label}")
    print("====================================================\n")

    group_out_dir = group_out_root / contrast_label
    group_out_dir.mkdir(exist_ok=True, parents=True)

    pattern = (
        f"sub-*/sub-*_task-{task_label}_space-{space_label}_"
        f"contrast-{contrast_label}_stat-effect_statmap.nii.gz"
    )

    effect_maps = sorted(firstlevel_dir.glob(pattern))
    if len(effect_maps) == 0:
        raise RuntimeError(
            f"No first-level maps found for contrast '{contrast_label}' with pattern:\n  {pattern}"
        )

    print(f"Found {len(effect_maps)} maps before QC.")

    # ----- QC: drop maps that are all-nan or constant -----
    good_maps = []
    good_subs = []
    for p in effect_maps:
        img = load_img(p)
        data = img.get_fdata()
        if not np.isfinite(data).any():
            print(f"[DROP] {p} is all non-finite.")
            continue
        if np.nanstd(data) == 0:
            print(f"[DROP] {p} is constant/zero.")
            continue
        good_maps.append(p)
        good_subs.append(p.name.split("_")[0].replace("sub-", ""))

    effect_maps = good_maps
    subject_labels = good_subs

    print(f"Kept {len(effect_maps)} maps after QC.")

    if len(effect_maps) < 2:
        raise RuntimeError(
            f"Need at least 2 valid subjects for group model of {contrast_label} "
            f"(found {len(effect_maps)})."
        )

    # Design matrix
    design_matrix = pd.DataFrame(
        {"intercept": [1.0] * len(effect_maps)},
        index=subject_labels,
    )

    # Fit second-level
    model = SecondLevelModel(mask_img=group_mask_img, minimize_memory=False)
    model = model.fit(effect_maps, design_matrix=design_matrix)

    # Save results
    contrasts = {group_contrast_name: "intercept"}

    save_glm_to_bids(
        model=model,
        contrasts=contrasts,
        out_dir=group_out_dir,
        threshold=0.001,          # <-- p-value threshold
        height_control="fpr",     # <-- interpret threshold as p
        cluster_threshold=10,
        bg_img=bg_img,
        two_sided=True,
    )

    print(f"\nSaved second-level outputs to:\n  {group_out_dir}\n")

