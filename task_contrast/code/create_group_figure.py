from pathlib import Path
from nilearn import plotting
from nilearn.image import load_img

# Paths to group maps
maps = {
    "twoBackMinusZeroBack": Path("/cbica/projects/executive_function/code/task_contrast/final/results_final_3/second-level/nback-rtdur/group-twoBackMinusZeroBack/group/contrast-twobackminuszeroback_stat-z_statmap.nii.gz"),
    "twoBack": Path("/cbica/projects/executive_function/code/task_contrast/final/results_final_3/second-level/nback-rtdur/group-twoBack/group/contrast-twoback_stat-z_statmap.nii.gz"),
    "zeroBack": Path("/cbica/projects/executive_function/code/task_contrast/final/results_final_3/second-level/nback-rtdur/group-zeroBack/group/contrast-zeroback_stat-z_statmap.nii.gz"),
    "PNC": Path("/cbica/projects/executive_function/code/task_contrast/final/task_contrast_PNC/group_zmap_MNI.nii.gz")
}

# Output directory
group_out_dir = Path("/cbica/projects/executive_function/code/task_contrast/final/figures")
group_out_dir.mkdir(parents=True, exist_ok=True)

# Background image
bg_img = load_img(
    "/cbica/projects/executive_function/.cache/templateflow/"
    "tpl-MNI152NLin6Asym/tpl-MNI152NLin6Asym_res-02_desc-brain_T1w.nii.gz"
)

# Titles for each map
titles = {
    "twoBackMinusZeroBack": "Group 2-back > 0-back",
    "twoBack": "Group 2-back",
    "zeroBack": "Group 0-back",
    "PNC": "PNC 2-back > 0-back"
}

# Loop through maps and plot
for key, path in maps.items():
    stat_img = load_img(path)

    plotting.plot_stat_map(
        stat_img,
        bg_img=bg_img,
        display_mode="z",
        cut_coords=(-36, -20, -6, 6, 30, 52, 64),
        threshold=3.29,
        black_bg=False,
        title=titles[key],
        output_file=str(group_out_dir / f"group_{key}_statmap.pdf"),
    )
