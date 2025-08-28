import glob
import pandas as pd
import numpy as np
import os

project_path = '/cbica/projects/executive_function/'
inpath_qc = project_path + 'EF_dataset/derivatives/xcpd_BABS_EF_full_project_outputs/xcpd'
outpath = project_path + 'EF_dataset_figures/concatenated_data/'

fileNames_qc = sorted(glob.glob(os.path.join(
    inpath_qc, 'sub-*', 'ses-*', 'func',
    'sub-*_ses-*_task-*_run-*_space-*_seg-4S1056Parcels_stat-coverage_bold.tsv'
)))

df_all = []

for fpath in fileNames_qc:
    # Load single-row coverage data
    df_qc = pd.read_csv(fpath, delimiter='\t')

    # Extract metadata from filename
    fname_parts = os.path.basename(fpath).split('_')
    metadata = {p.split('-')[0]: p.split('-')[1] for p in fname_parts[:-1]}  # skip .tsv part

    # Combine metadata and QC values into one row
    df_row = pd.DataFrame({**metadata, **df_qc.to_dict(orient='records')[0]}, index=[0])
    df_all.append(df_row)

# Combine all rows
df_main_qc = pd.concat(df_all, ignore_index=True)

# Save
os.makedirs(outpath, exist_ok=True)
df_main_qc.to_csv(os.path.join(outpath, 'concat_xcpd_qc_coverage.csv'), index=False)

