#!/usr/bin/env python
"""Create PDF figures from thresholded second-level z maps."""

from pathlib import Path

from nilearn import plotting
from nilearn.image import load_img


MODEL_TYPE = "rtdur"

maps = {
    "twoBackMinusZeroBack": Path(
        f"/cbica/projects/executive_function/code/task_contrast/final/results_final_3/"
        f"second-level/nback-{MODEL_TYPE}/group-twoBackMinusZeroBack/group/thresholded/"
        f"contrast-twobackminuszeroback_stat-z_thresholded_statmap.nii.gz"
    ),
    "twoBack": Path(
        f"/cbica/projects/executive_function/code/task_contrast/final/results_final_3/"
        f"second-level/nback-{MODEL_TYPE}/group-twoBack/group/thresholded/"
        f"contrast-twoback_stat-z_thresholded_statmap.nii.gz"
    ),
    "zeroBack": Path(
        f"/cbica/projects/executive_function/code/task_contrast/final/results_final_3/"
        f"second-level/nback-{MODEL_TYPE}/group-zeroBack/group/thresholded/"
        f"contrast-zeroback_stat-z_thresholded_statmap.nii.gz"
    ),
}

titles = {
    "twoBackMinusZeroBack": "Group 2-back > 0-back",
    "twoBack": "Group 2-back",
    "zeroBack": "Group 0-back",
}

group_out_dir = Path(
    "/cbica/projects/executive_function/code/task_contrast/final/"
    "figures/thresholded_group_maps"
)
group_out_dir.mkdir(parents=True, exist_ok=True)

bg_img = load_img(
    "/cbica/projects/executive_function/.cache/templateflow/"
    "tpl-MNI152NLin6Asym/tpl-MNI152NLin6Asym_res-02_desc-brain_T1w.nii.gz"
)

for key, path in maps.items():
    if not path.exists():
        print(f"[SKIP] Missing file: {path}")
        continue

    stat_img = load_img(path)

    plotting.plot_stat_map(
        stat_img,
        bg_img=bg_img,
        display_mode="z",
        cut_coords=(-36, -20, -6, 6, 30, 52, 64),
        threshold=1e-6,  # hides zeros only
        vmax=8,
        symmetric_cbar=True,
        black_bg=False,
        title=titles[key],
        output_file=str(group_out_dir / f"group_{MODEL_TYPE}_{key}_thresholded_zmap.pdf"),
    )

print(f"\nSaved thresholded group figures to:\n  {group_out_dir}\n")
