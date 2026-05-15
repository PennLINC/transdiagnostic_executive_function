#!/usr/bin/env python
"""Run first-level GLM for n-back task within a single subject."""

import sys
from pathlib import Path

import pandas as pd
from scipy.stats import norm
from nilearn.glm.first_level import first_level_from_bids
from nilearn.interfaces.bids import save_glm_to_bids


def collapse_events_to_blocks(events: pd.DataFrame) -> pd.DataFrame:
    """
    Collapse trial-level n-back events into one row per consecutive block.

    Expected input columns include:
      onset, duration, trial_type

    Output:
      one row per block with:
        onset    = onset of first event in the block
        duration = sum of durations in the block
        trial_type = block label
    """
    events = events.sort_values("onset").reset_index(drop=True).copy()

    if events.empty:
        return events

    # New block whenever trial_type changes
    block_id = (events["trial_type"] != events["trial_type"].shift()).cumsum()

    block_events = (
        events.groupby(block_id, as_index=False)
        .agg(
            onset=("onset", "first"),
            duration=("duration", "sum"),
            trial_type=("trial_type", "first"),
        )
        .sort_values("onset")
        .reset_index(drop=True)
    )

    return block_events


def label_lsa_blocks(
    events: pd.DataFrame,
    conditions_to_split=("zero_back", "two_back"),
    delimiter="__",
) -> pd.DataFrame:
    """
    Relabel selected block events for Least Squares-All (LSA) modeling.

    Each block of each selected condition receives a unique trial_type,
    e.g. zero_back__001, zero_back__002, two_back__001, etc.
    Non-selected conditions, such as instruction, are left unchanged.
    """
    events = events.copy()
    condition_counter = {condition: 0 for condition in conditions_to_split}

    for row_idx, row in events.iterrows():
        condition = row["trial_type"]
        if condition not in condition_counter:
            continue

        condition_counter[condition] += 1
        events.loc[row_idx, "trial_type"] = (
            f"{condition}{delimiter}{condition_counter[condition]:03d}"
        )

    return events


def average_contrast_expression(design_columns, condition_prefix: str) -> str:
    """Return an expression averaging all LSA regressors for a condition."""
    condition_columns = [
        column for column in design_columns if column.startswith(f"{condition_prefix}__")
    ]
    if len(condition_columns) == 0:
        raise RuntimeError(
            f"No LSA regressors found for condition prefix '{condition_prefix}'."
        )

    return " + ".join(f"({column}) / {len(condition_columns)}" for column in condition_columns)


def lsa_regressor_columns(design_columns, condition_prefixes=("zero_back", "two_back")):
    """Return the individual LSA regressor columns to export as beta maps."""
    prefixes = tuple(f"{prefix}__" for prefix in condition_prefixes)
    return [column for column in design_columns if column.startswith(prefixes)]


def export_individual_beta_maps(model, design_columns, beta_series_dir: Path, sub_id: str):
    """Save one effect-size beta map for each individual LSA block regressor."""
    beta_out_dir = beta_series_dir / f"sub-{sub_id}"
    beta_out_dir.mkdir(parents=True, exist_ok=True)

    beta_rows = []
    beta_columns = lsa_regressor_columns(design_columns)
    if len(beta_columns) == 0:
        raise RuntimeError("No individual LSA beta regressors found to export.")

    print(f"\nExporting {len(beta_columns)} individual LSA beta maps to:")
    print(f"  {beta_out_dir}")

    for column in beta_columns:
        beta_img = model.compute_contrast(column, output_type="effect_size")
        beta_path = (
            beta_out_dir
            / f"sub-{sub_id}_task-nback_space-MNI152NLin6Asym_"
            f"contrast-{column}_stat-effect_statmap.nii.gz"
        )
        beta_img.to_filename(beta_path)

        condition, block_number = column.split("__", 1)
        beta_rows.append(
            {
                "subject": sub_id,
                "condition": condition,
                "block": block_number,
                "regressor": column,
                "beta_map": str(beta_path),
            }
        )
        print(f"  Saved {column}: {beta_path.name}")

    beta_index_path = beta_out_dir / f"sub-{sub_id}_task-nback_beta-series_index.tsv"
    pd.DataFrame(beta_rows).to_csv(beta_index_path, sep="\t", index=False)
    print(f"Saved beta-series index TSV:\n  {beta_index_path}")


# ============================================================
# GET SUBJECT FROM COMMAND LINE
# ============================================================
sub_id = sys.argv[1]  # subject passed by SLURM array / CLI
sub_labels = [sub_id]  # nilearn expects a list

print(f"Running first-level GLM for subject: {sub_id}")

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

# ============================================================
# FIND FMRIPREP BRAIN MASK FOR THIS SUBJECT
# ============================================================
# Example expected filename:
# sub-21050_ses-1_task-nback_run-01_space-MNI152NLin6Asym_res-2_desc-brain_mask.nii.gz
# or sub-20259_ses-3_task-nback_acq-VARIANTObliquity_run-01_space-MNI152NLin6Asym_res-2_desc-brain_mask.nii.gz
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
    # Since only one run per subject, take the first match
    mask_img = str(mask_candidates[0])
    print(f"Using fMRIPrep brain mask for sub-{sub_id}:\n  {mask_img}\n")

# ============================================================
# BUILD FIRST-LEVEL MODEL FROM BIDS
# ============================================================
results_root = Path(
    "/cbica/projects/executive_function/code/task_contrast/final/"
    "results_beta_series"
)

# Group-ready first-level contrast outputs from the LSA model.
out_dir = results_root / "first-level" / "nback-block-lsa"

# True beta-series outputs: one beta map per 0-back/2-back block regressor.
beta_series_dir = results_root / "beta_series"

# Modified events files used for the LSA model.
debug_events_dir = results_root / "debug_events" / f"sub-{sub_id}"

out_dir.mkdir(parents=True, exist_ok=True)
beta_series_dir.mkdir(parents=True, exist_ok=True)
debug_events_dir.mkdir(parents=True, exist_ok=True)

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
    smoothing_fwhm=5.0,
    n_jobs=4,
    verbose=1,
    drift_model="cosine",
    high_pass=0.005,
    confounds_strategy=("motion", "non_steady_state"),
    confounds_motion="basic",
    #confounds_compcor="anat_combined",
    #confounds_n_compcor=5,
    # Use fMRIPrep mask if found; otherwise None (Nilearn auto-mask)
    mask_img=mask_img,
)

# Single subject
model = models[0]
run_imgs = models_run_imgs[0]
events_list = models_events[0]
confounds_list = models_confounds[0]

updated_events_list = []
debug_dir = debug_events_dir

for run_idx, events in enumerate(events_list, start=1):
    events = events.copy()

    # Rename trial_type labels before building design matrix
    if "trial_type" in events.columns:
        events["trial_type"] = events["trial_type"].replace(
            {
                "0BACK": "zero_back",
                "2BACK": "two_back",
                "INSTRUCTION": "instruction",
            }
        )

    # Collapse trial-level events into one row per block
    events = collapse_events_to_blocks(events)

    print(f"\nCollapsed events for run {run_idx}:")
    print(events)
    print(f"Number of rows after collapsing: {len(events)}")

    expected_trial_types = {"instruction", "zero_back", "two_back"}
    assert set(events["trial_type"]).issubset(expected_trial_types), (
        f"Unexpected trial types after collapsing: {set(events['trial_type'])}"
    )
    assert len(events) == 12, f"Expected 12 blocks, got {len(events)}"

    # LSA: make each 0-back and 2-back block its own regressor.
    # Instructions remain pooled as before.
    events = label_lsa_blocks(events)

    print(f"\nLSA-labeled events for run {run_idx}:")
    print(events)

    debug_path = debug_dir / f"sub-{sub_id}_run-{run_idx:02d}_lsa_events.tsv"
    events.to_csv(debug_path, sep="\t", index=False)
    print(f"Saved LSA events debug TSV:\n  {debug_path}")

    updated_events_list.append(events)

print(f"Number of runs for subject {sub_id}: {len(run_imgs)}")
print("Confounds entries for each run:")
for i, c in enumerate(confounds_list):
    print(f"  Run {i}: {c}")

# ---------- FIT MODEL ----------

model.minimize_memory = False

print(f"\nFitting LSA block GLM for subject {sub_id}...")
model = model.fit(
    run_imgs,
    events=updated_events_list,
    confounds=confounds_list,
)

# Inspect design matrix
design_matrix = model.design_matrices_[0]
print("\nDesign matrix columns:")
print(design_matrix.columns)
print(f"\nTotal # regressors in design matrix: {design_matrix.shape[1]}")

# Average the LSA block regressors back into group-ready contrasts.
# This preserves the same output labels expected by the second-level script:
#   twoBack, zeroBack, twoBackMinusZeroBack, instruction
#
# ALSO add individual LSA block-vs-baseline contrasts to save_glm_to_bids:
#   zero_back__001, zero_back__002, zero_back__003, ...
#   two_back__001, two_back__002, two_back__003, ...
# These individual contrasts should appear in the Nilearn HTML report too.
two_back_expr = average_contrast_expression(design_matrix.columns, "two_back")
zero_back_expr = average_contrast_expression(design_matrix.columns, "zero_back")
two_back_minus_zero_back_expr = f"({two_back_expr}) - ({zero_back_expr})"

individual_lsa_contrasts = {}
for column in lsa_regressor_columns(design_matrix.columns):
    # Contrast name and expression are both the individual design-matrix column,
    # so each one is a single block-vs-baseline map.
    individual_lsa_contrasts[column] = column

contrasts = {
    "two_back": two_back_expr,
    "zero_back": zero_back_expr,
    "two_back - zero_back": two_back_minus_zero_back_expr,
    "instruction": "instruction",
    **individual_lsa_contrasts,
}

print(f"\nAdded {len(individual_lsa_contrasts)} individual LSA block contrasts to save_glm_to_bids.")

print("\nContrasts:")
for contrast_name, contrast_expr in contrasts.items():
    print(f"  {contrast_name}: {contrast_expr}")

save_glm_to_bids(
    model,
    contrasts=contrasts,
    contrast_types={contrast_name: "t" for contrast_name in contrasts},
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

# Also export the individual LSA beta-series maps.
# These are separate block-vs-baseline effect-size maps, one per 0-back/2-back block.
export_individual_beta_maps(
    model=model,
    design_columns=design_matrix.columns,
    beta_series_dir=beta_series_dir,
    sub_id=sub_id,
)

print("\nDone.\n")

