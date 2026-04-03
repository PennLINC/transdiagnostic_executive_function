from pathlib import Path
from nilearn import plotting
from nilearn.image import load_img

# Path to output directory
out_dir = Path("/cbica/projects/executive_function/code/task_contrast/final/figures")

bg_img = load_img(
    "/cbica/projects/executive_function/.cache/templateflow/"
    "tpl-MNI152NLin6Asym/tpl-MNI152NLin6Asym_res-02_desc-brain_T1w.nii.gz"
)

MODEL_TYPES = ["nback-nortdur", "nback-rtdur"]

CONTRASTS = [
    {
        "contrast_dir": "group-twoBackMinusZeroBack",
        "stat_file": "contrast-twobackminuszeroback_stat-z_statmap.nii.gz",
        "title": "2-back > 0-back",
        "label": "twoBackMinusZeroBack",
    },
    {
        "contrast_dir": "group-twoBack",
        "stat_file": "contrast-twoback_stat-z_statmap.nii.gz",
        "title": "2-back > baseline",
        "label": "twoBack",
    },
    {
        "contrast_dir": "group-zeroBack",
        "stat_file": "contrast-zeroback_stat-z_statmap.nii.gz",
        "title": "0-back > baseline",
        "label": "zeroBack",
    },
]

for model_type in MODEL_TYPES:
    for contrast in CONTRASTS:

        group_zmap = Path(
            "/cbica/projects/executive_function/code/task_contrast/final/results/second-level"
        ) / model_type / contrast["contrast_dir"] / "group" / contrast["stat_file"]

        stat_img = load_img(group_zmap)
   
        model_label = "RTDur" if model_type == "nback-rtdur" else "noRTDur"

        plotting.plot_stat_map(
            stat_img,
            bg_img=bg_img,
            display_mode="z",
            cut_coords=(-36, -20, -6, 6, 30, 52, 64),
            threshold=3.09,
            black_bg=False,
            title=f"{model_label}: {contrast['title']}",
            output_file=str(
                out_dir
                / f"{model_label}_{contrast['label']}_statmap.pdf"
            ),
        )
