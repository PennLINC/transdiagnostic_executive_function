# Cubic Organization: /cbica/projects/executive_function
*** denotes an especially important directory

+ `apptainer` folder contains apptainer datasets with sif files from each BIDS app used for preprocessing
+ `apptainer-datasets` folder contains the datalad dataset version of each containerized BIDS app. This is the version used when creating a new BABS project.
+ `code`
    + `phenotype_analysis` contains code for CNB, clinical, and diagnostic data
        + `clinical` contains code, data, and figures related to clinical diagnostic data
        + `CNB` contains code and data related to CNB tasks
        + `participant_demographics` contains code and data related to demographic info
    + `heudiconv` contains scripts to use heudiconv to convert raw neuroimaging data to BIDS (including a reconversion after finding an error in the first heuristic file)
    + `count_longitudinal_sessions` contains scripts that count the number of imaging sessions and distance between longitudinal sessions, and a csv file that summarizes what date each participant had their first scan
    + `flywheel` contains scripts to get original raw data from Flywheel onto Cubic
    + `curation` ***
        +`babs_curation` contains scripts needed for BABS preprocessing
        + `cubids_curation` contains Python scripts used to make edits to neuroimaging metadata suggested from Cubids phase that could not be accomplished with bash terminal commands in Cubids software
    + `image_processing` ***
        + `QC` contains scripts to concatenate QC data into a usable form
        + `unzip` contains scripts to unzip relevant files from processing outputs needed for QC and analysis/figure-making
    + `T1_QC` *** contains scripts needed to create T1 QC slices for manual ratings 
    + `task_contrast` / `final` *** is a subdirectory related to task contrast analyses. Many deleted. final one is results_final_3_edited
        + `code` contains scripts for running first and second level GLMs, as well as code for creating group figures, creating tables to understand the data, plot timeseries, and summarize logs and performance. Used to to contain results from running different models/versions, but now only contains scripts related to our final model: results_final_3_edited
            + `qc_outputs` contains outputs of running `qc_nback_attention.py` to investigate the attention of participants during the nback task
        + `behavioral` contains summary tsv files of performance and TRs per condition
        + `figures` contains final figures for paper from running scripts in `code`
        + `task_contrast_exclusions.csv` contains sessions that did not successfully undergo first-level task contrast GLMs and were not included in the group task contrast maps
        + `task_contrast_PNC` contains task contrast data from PNC to be used in comparison with EF task contrast data
        + `compare_EF_PNC` contains scripts and output figures of comparing EF task contrast data with PNC task contrast data
        + `results_final_3_edited` contains results of running the final version of first and second level GLMs
            + `first-level`
                + `nback-nortdur` contains subject-level directories, result of running without RTDur model
                + `nback-rtdur` contains subject-level directories, result of running with RTDur model
            + `second-level`
                + `nback-nortdur`
                    + `group-twoBack` contains 2back - implicit baseline results
                    + `group-twoBackMinusZeroBack` contains 2back - 0back results
                    + `group-zeroBack` contains 0back - implicit baseline results
                + `nback-rtdur`
                    + `group-twoBack` contains 2back - implicit baseline results
                    + `group-twoBackMinusZeroBack` contains 2back - 0back results
                    + `group-zeroBack` contains 0back - implicit baseline results
+ `data' / `bids`
    + `ds007116` and `git-annex-remote-openneuro` are used to help with uploading files from BIDS dataset to openneuro
    + `EF_bids_data` contains BIDS-ified neuroimaging data (not datalad-tracked, includes some info that cannot be shared)
    + `EF_bids_data_reconverted` is a directory of subjects with reconverted BIDS data after catching a mistake in the first heuristic file and running heudiconv with the new heuristic file
    + `EF_bids_data_DataLad` *** is the main BIDS datalad dataset that is updated and maintained; used for subsequent processing and analysis
    + participants_scanned.csv is a csv file that keeps track of each participant ID and the number of sessions they were scanned
    + `Exemplar_Dataset` is the exemplar dataset for CuBIDS
    +  `original_scans_tsv` contains the original scans.tsv files without information that was removed before adding to Datalad-tracked dataset, in case you need to look at info like acq_time that cannot be Datalad-tracked
    +  `sourcedata`/`EFR01` *** contains the original data raw/non-BIDS-ified neuroimaging data downloaded from flywheel
    +  `old_datalad_ds_to_remove` contains old Datalad datasets that can be removed, but encountered a permissions error
+ `Data_Management.txt` contains details of cubic project
+ `dropbox` contains files transferred from local computer --> cubic. They are usually moved to the appropriate folder after landing in dropbox; this is used because the local computer cannot interact with other directories on cubic.
+ `EF_dataset` ***
    + `braindr` contains the axial and sagittal png slices for each subject used to manually rate T1 scans
    + `code` contains config files for running BABS projects for each modality/BIDS App
    + `derivatives` contains the full BABS projects for each modality and project outputs (zipped and unzipped for uploading to OpenNeuro)
+ `EF_dataset_figures` ***
    + `concatenated_data` contains csv files, pdf files, and png files for QC metrics for each modality
    + `figures` contains folders for each modality with pdf/png/nifti files used to generate figures for paper
        + `aslprep_figures`
        + `atlas_figure`
        + `fmriprep_figures`
        + `qsi_figures` (note bundle data was run locally, so not on cubic; this just includes scalar data)
        + `xcpd_group_maps`
    + `processing_scripts` contains scripts used to run analyses/summaries/make images for figures for the paper. It also includes csv files listing the scans excluded from each analysis/image.
+ `mamba` and `matlab`, and  `miniforge3` are all folders to help set up environments & matlab
+ `mebold_trt` contains another project's data and code - multi-echo/single-echo data descriptor paper
+ `neuromaps-data` and `nnt-data` contains downloaded data from neuromaps and net neuro tools
+ `python_requirements` contains txt files with python requirements for different environments
+ `RAW` is directory to store raw DICOM files uploaded to CBICA PACS server - irrelevant for this project but cannot delete from cubic project
+ `software` contains downloaded software necessary for this project, and `misc_env_software_downloads` contains additional random downloads related to environments or software
+ `task_contrast_openneuro_edited` contains the final directory structure of task contrast derivatives to be uploaded to openneuro
+ `task_events_files` contains original files from running nback task on the MRI scanner (used to troubleshoot task contrast analyses)
+ `templateflow` contains standardized neuroimaging templates used by neuroimaging processing/analysis tools; each folder is one template space
+ `tien` contains directory with code from a workshop project that uses EF dataset
+ 




### Overview of data structure on cubic:
```
/cbica/projects/executive_function/
    |-  code/           # Local clone of the GitHub repository
        |- curation     # Scripts for BIDS curation
        |-  figures/    # Any figures for the manuscript
        |_  data/       # Tabular data that may be shared on GitHub
    |-  data/
    |-  results/        # Results that cannot be shared on GitHub
    |_  reproduction/
        |-  code/       # Local clone of reproducibilibuddy's fork of GitHub repository
        |-  data/       # Any data that must be copied and not referenced
        |_  results/
```
