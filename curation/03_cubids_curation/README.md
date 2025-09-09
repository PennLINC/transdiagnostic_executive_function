The Python scripts here are used to update, edit, or correct metadata in the DataLad-tracked EF dataset.
+ The scripts are run in terminal in cubic by calling `python {name of script}` and then tracking changes with `datalad save -m "{commit message}"`
  after the script is finished running.
+ These python scripts are ordered in the order in which we ran the scripts on the dataset.
+ Unordered scripts include: `config.yml` which is the custom configuration file we used for running `cubids group` and `cubids apply` commands; `cubids_apply.sh` that is an optional bash script used to submit `cubids apply` as a job since it takes a while to run; and `cubids_summary_counts.Rmd` that calculates the percentage of dominant and variant scans for each type of scan.
+ The `final_cubids_docs` folder contains the final versions of all the output documents from running CuBIDS; all versions can be found in the dataset on OpenNeuro.

Note about repeated runs in the dataset:
+ There are some scans with an extra run in the dataset, if it was re-done at the scanner. While T1 scans should have 1 run, T2 scans should have 1 run, DWI scans should have 1 run, fMRI rest scans should have 2 runs, fMRI n-back scans should have 1 run, fmaps should each have 1 run, and ASL/M0 scans should have 1 run each, there are instances where a session has an extra second and/or third run.
+ During the curation process, during the `cubids apply` stage, runs with low volumes were automatically deleted. Other repeated runs were manually investigated and discussed with the study team, then manually deleted if it was determined that one of the runs was of poor quality.
+ The repeated runs that were manually deleted were re-named in sequential order such that the remaining runs were either 'run 1' or 'run 1' and 'run 2'. However, repeated runs automatically deleted as part of the `cubids apply` stage were not always re-named in sequential order, such that there can exist a sole 'run 2' or 'run 2' and 'run 3'.
+ Some repeated runs were intentionally kept in the dataset if none of the scans were determined to be of poor quality. Hence, there can remain extra repeated runs in the dataset.
