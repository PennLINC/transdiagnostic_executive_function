The Python scripts here are used to update, edit, or correct metadata in the DataLad-tracked EF dataset.
+ The scripts are run in terminal in cubic by calling `python {name of script}` and then tracking changes with `datalad save -m "{commit message}"`
  after the script is finished running.
+ These python scripts are ordered in the order in which we ran the scripts on the dataset.
+ Unordered scripts include: `config.yml` which is the custom configuration file we used for running `cubids group` and `cubids apply` commands; `cubids_apply.sh` that is an optional bash script used to submit `cubids apply` as a job since it takes a while to run; and `cubids_summary_counts.Rmd` that calculates the percentage of dominant and variant scans for each type of scan.
+ The `final_cubids_docs` folder contains the final versions of all the output documents from running CuBIDS; all versions can be found in the dataset on OpenNeuro.
