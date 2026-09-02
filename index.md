---
layout: default
title: Transdiagnostic Executive Function
parent: Documentation
has_children: false
has_toc: false
nav_order: 3
---


### Project Title

Transdiagnostic Executive Function
A longitudinal data resource to study brain development and transdiagnostic variation in executive function

### Brief Project Description
Executive function (EF) is a crucial aspect of human development.
Deficits in EF that emerge in adolescence represent a transdiagnostic symptom associated with many
forms of psychopathology, including attention deficit hyperactivity disorder (ADHD) and psychosis-
spectrum (PS).
There are relatively few open data resources specifically tailored to evaluate the development of EF across
clinical diagnoses. Here, we introduce a new data resource that combines longitudinal multi-modal
imaging data (sMRI, dMRI, resting-state and task fMRI, & ASL) with rich clinical and cognitive phenotyping data.

### Project Lead

Brooke L. Sevchik

### Faculty Lead

Theodore D. Satterthwaite

### Collaborators

Brooke L. Sevchik, Golia Shafiei, Kristin Murtha, Sophia Linguiti, Lia Brodrick, Juliette B.H. Brook, Matt Cieslak, Elizabeth Flook, Kahini Mehta, Steven L. Meisler, Kosha Ruparel, Sage Rush, Taylor Salo, S. Parker Singleton, Tien T. Tong, Mrugank Salunke, Dani S. Bassett, Monica E. Calkins, Mark A. Elliott, Raquel E. Gur, Ruben C. Gur, Tyler M. Moore, J. Cobb Scott, Russell T. Shinohara, M. Dylan Tisdall, Daniel H. Wolf, David R. Roalf, Theodore D. Satterthwaite

### Project Start Date

September 2024

### Current Project Status

Completed (July 2026)

### Corresponding Publication
<https://doi.org/10.1038/s41597-026-08095-1>

### Github repo

<https://github.com/PennLINC/transdiagnostic_executive_function>

### Path to data on filesystem

/cbica/projects/executive_function

### Slack Channel

#efr01_grmpyr01_opendata

### Conference presentations

- Flux Congress, September 2025

### Code documentation

General overview of project/data organization steps are below, including information about the scripts necessary for each step in the workflow and the folders in which they can be found in the corresponding GitHub repository. Specific details about scripts and individual steps can be found
in the README.md files in each folder in the corresponding GitHub repository.

Imaging Data:
1. Download the data from Flywheel project using fw sync
   + `/curation/01_call_fw_sync.sh`
2. Create a heuristic file and use HeuDiConv to convert dicom files to NIfTI files, and organize data in BIDS format.
   + `/curation/02_heudiconv_conversion/01_heuristic.py` and `02_heudiconv_conversion/02_heuristic_reconvert.py` contain necessary heuristic files
   + `/curation/02_heudiconv_conversion/02_convert_all_heudiconv.sh` and `02_heudiconv_converstion/02_convert_all_heudiconv_reconvert.sh` contain necessary bash scripts that use the heuristic file to convert dicoms to NIfTIs in BIDS format.
3. Use CuBIDS software to fix incorrect metadata, add in missing metadata, clean metadata, delete unecessary repeated runs of scans, ensure correct BIDS format, summarize the heterogeneity in the dataset, and organize scans into different acquisition groups based on their metadata.
   + `/curation/03_cubids_curation/` contains Python scripts used to edit metadata in dataset, as well as the configuration `config.yml` for CuBIDS software
   + `/curation/03_cubids_curation/final_cubids_docs` contains the final output files from running CuBIDS
4. Anonymize scans (reface T1 scans & deface T2 scans) using AFNI's refacer and pydeface.
   + `/curation/04_reface_anatomicals.sh`
5. Preprocess the imaging data using BABS software.
   + `/preprocessing/babs_yaml_files` contains the yaml files for each BIDS App we ran
   + `/preprocessing/make_container_babs.sh` is an optional helper script to make a container for BIDS Apps
9. Complete quality control (using python scripts to concatenate data from individual scans into summary csv files and visualize the distribution of QC metrics for each modality) on the preprocessed scans and note which images are of poor quality or high quality.
    + `/analysis/unzip` folder contains some scripts necessary to unzip the files needed to grab the QC metrics for each modality, which should be run before the scripts in `QC/qc_scripts`
    + `/QC/qc_scripts` contains the Python scripts necessary for generating concatenated csv files with QC metrics for each modality and visualize distributions of the QC metrics, as well as a script to create and visualize the slices necessary for manual T1 QC ratings
    + `/QC/qc_csvs` and `/QC/qc_distribution_figs` contain the csv files and plots that are the output of scripts in `/QC/qc_scripts`
    + `/QC` folder also contains csv files with a list of the exclusions resulting from QC decisions, which are then used in later Python scripts used to create group average figures to exclude those scans or regions from the group average.
11. Create final group average figures for publication using Python scripts. Scans that were rated as poor quality (did not pass QC) are not included in the final group average figures.
    + `/analysis/01_unzip` contains scripts necessary to unzip the files for individual scans needed to create the group average plots. This should be run before the plotting scripts
    + `/analysis/02_plot` contains scripts used to create group average plots and maps, as well as a script to create the reconstructed tracts for a subset of subjects
    + `/neuroimaging_figures` contains the figures that are the output of running the scripts in `/analysis/02_plot`, organized by imaging modality

Clinical and Demographic Data:
1. Clean and organize clinical data into usable format. Consult with other members of team to correct any mistakes in original clinical data. Visualize clinical diagnoses (sankey plot).
   + `/clinical/clinical_data_cleaning.Rmd` cleans the data, investigates potential errors in the data, and corrects mistakes
   + `/clinical/clinical_diagnostic_distribution.Rmd` summarizes clinical diagnostic information and produces the sankey plot visualization stored in `/clinical/clinical_figures`
3. Clean and organize demographic data into usable format. Consult with other members of team to correct any mistakes in original demographic data. Visualize demographic info with bar plots and histograms.
   + `/demographics/demographics_org.Rmd` organizes, summarizes, and plots demographics data, as well as corrects any mistakes in original demographic data. The resulting plots are stored in `/demographics/demographic_figures`

Cognitive Data:
1. Organize and clean data from CNB. Consult with members of team to resolve any errors or weird formatting. Report missingness.
2. Use `cognitive/CNB_transformation_script_EF.Rmd` to create a format that is consistent with the National Institute of Mental Health Data Archive and produce separate tsv files for each cognitive task. These resulting files with their corresponding JSON files can be found in the `phenotype` folder [here](https://openneuro.org/datasets/ds007116).

Self-Report Data:
1. Clean and organize self-report data. Separate self-report csv into separate tsv files for each scale. Consult with original sources and other members of team to learn scoring strategy for each scale.
2. Score each script.
   + `self-report` contains all the R Markdown scripts used to score each scale. The resulting tsv files with their corresponding JSON files can be found in the `phenotype` folder [here](https://openneuro.org/datasets/ds007116).

Task Contrast:
1. Create events.tsv files and corresponding JSON files for each subject/session that did the nback task using log files from Flywheel.
   + Details about this process and scripts can be found in `curation/05_nback_scoring'.
2. Run first and second-level GLMs in Nilearn.
   + Get list of subjects that had nback data and passed QC to use in first-level scripts using `task_contrast/get_nback_subjects.Rmd`
   + Scripts found in `task_contrast/code`.
   + Scripts used to run QC checks found in `task_contrast/QC`
4. Create group figures from second-level results.
   + Scripts found in `task_contrast/code`.
   + Output figures found in `task_contrast/results`
5. Compare 2back>0back results in this dataset with 2back>0back results from the Philadelphia Neurodevelopmental Cohort.
   + Script found in `task_contrast/compare_EF_PNC`
   + Scatterplot of comparison found in `task_contrast/results/EF_PNC_scatterplot.pdf`

