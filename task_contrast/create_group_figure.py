from pathlib import Path
from nilearn import plotting
from nilearn.image import load_img

# Path to group map (output of second-level GLM)
group_zmap = Path(
    "/cbica/projects/executive_function/EF_dataset/derivatives/nback-rtdur/"
    "group-twoBackMinusZeroBack/contrast-twoBackMinusZeroBack_stat-z_statmap.nii.gz"
)

# Path to output directory
out_dir = Path("/cbica/projects/executive_function/code/task_contrast")

stat_img = load_img(group_zmap)

bg_img = load_img(
    "/cbica/projects/executive_function/.cache/templateflow/"
    "tpl-MNI152NLin6Asym/tpl-MNI152NLin6Asym_res-02_desc-brain_T1w.nii.gz"
)

# Make a figure & save as vector PDF
plotting.plot_stat_map(
    stat_img,
    bg_img=bg_img,  # same T1 background loaded earlier
    display_mode="z",  # or "ortho", "yx", "mosaic", etc.
    cut_coords=(-36, -20, -6, 6, 30, 52, 64),
    threshold=3.09,
    black_bg=False,
    title="Group 2-back > 0-back",
    output_file=str(out_dir / "group_twoBackMinusZeroBack_statmap.pdf"),
)
