---
layout: default
title: Transdiagnostic Executive Function
parent: Documentation
has_children: false
has_toc: false
nav_order: 3
---


### Project Title

Transdiagnostic Executive Function: An Open, Fully Processed, Longitudinal Data Resource

### Brief Project Description
Executive function (EF) is a crucial aspect of human development.
Deficits in EF that emerge in adolescence represent a transdiagnostic symptom associated with many
forms of psychopathology, including attention deficit hyperactivity disorder (ADHD) and psychosis-
spectrum (PS).
There are relatively few open data resources specifically tailored to evaluate the development of EF across
clinical diagnoses. Here, we introduce a new data resource that combines longitudinal multi-modal
imaging data (sMRI, dMRI, fMRI, ASL, & QSM) with rich clinical and cognitive phenotyping data.

### Project Lead

Brooke L. Sevchik

### Faculty Lead

Theodore D. Satterthwaite

### Collaborators

Golia Shafiei, Kristin Murtha, Juliette B.H. Brook, Lia Brodrick, Kahini Mehta, Sage Rush,
Matt Cieslak, Steven L. Meisler, Taylor Salo, S. Parker Singleton, Tien T. Tong, Mrugank Salunke, Dani S. Bassett, Monica E. Calkins, Mark A. Elliott, Raquel E. Gur, Ruben C. Gur, Tyler M. Moore, Kosha Ruparel, Russell T. Shinohara, M. Dylan Tisdall, Daniel H. Wolf, David R. Roalf, Theodore D. Satterthwaite

### Project Start Date

September 2024

### Current Project Status

In preparation

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
   + Note that MEGRE sequences for QSM were not preprocessed; we did not run any BIDS Apps on them through BABS
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
   + `/clinical/clinical_diagnostic_distribution.Rmd` summarizes clinical diagnostic information and produces the sankey plot visualization stored in `/clinical/clinical_figures`
3. Clean and organize demographic data into usable format. Consult with other members of team to correct any mistakes in original demographic data. Visualize demographic info with bar plots and histograms.
   + `/demographics/demographics_org.Rmd` organizes, summarizes, and plots demographics data, as well as corrects any mistakes in original demographic data. The resulting plots are stored in `/demographics/demographic_figures`




