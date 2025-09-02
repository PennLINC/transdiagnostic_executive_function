The environment used for these scripts is the `babs` environment, for which the python requirements can be found in `/python_requirements/babs_requirements`

The QC scripts contained here include:
+ Python scripts that concatenate data from individual preprocessing outputs to create csv files (in the `qc_csvs` folder) and distribution figures
  (in `qc_distribution_figs` folder) that are used to make QC pass/fail decisions after discussion with team members.
+ `T1_QC_slices.ipynb` creates and visually displays the slices used to manually evaluate T1 scans for QC.
+ `fmri_coverage.Rmd` is used to investigate more details about the scans that have coverage <50%.
+ `excluded_scans_*.csv` are scans that did NOT pass QC and are later passed into python scripts in the analysis folder to exclude these scans from group average plots.
+ `/QC/qc_csvs/qc_summary.csv` contains a summary record of which scans for which modalities are recommended 'passes' versus 'fails' based on our criteria for high quality vs. poor quality scans

All scans regardless of pass/fail status are included in the raw dataset.
