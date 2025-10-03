The environment used for these scripts is the `babs` environment, for which the python requirements can be found in `/python_requirements/babs_requirements`

The QC scripts contained here include:
+ Python scripts that concatenate data from individual preprocessing outputs to create csv files (in the `qc_csvs/full_concatenated_csvs` folder) and distribution figures
  (in `qc_distribution_figs` folder) that are used to make QC pass/fail decisions after discussion with team members.
+ `qc_scripts/create_T1_QC_slices.ipynb` creates and visually displays the slices used to manually evaluate T1 scans for QC.
+ `qc_scripts/fmri_coverage.Rmd` is used to investigate more details about the scans that have coverage <50%.
+ `excluded_csvs/excluded_scans_*.csv` are scans that did NOT pass QC and are later passed into python scripts in the analysis folder to exclude these scans from group average plots.
+ `qc_csvs/final_QC_csvs` is a folder that contains a summary record of which scans for which modalities are recommended 'passes' versus 'fails' based on our criteria for high quality vs. poor quality scans. There is a separate csv file for each modality, including both the variable used to determine the QC threshold for that modality and the QC determination for each subjects/session. Each csvs file is accompanied by a json file explaining the data it contains.
  + Note that for fMRI and ASL data, T1 QC recommendations should also be taken into account.
+ `QC_distributions.Rmd` contains code that summarizes the amount of participants and scans/sessions that passed vs. failed each modality.

All scans regardless of pass/fail status are included in the raw dataset.
