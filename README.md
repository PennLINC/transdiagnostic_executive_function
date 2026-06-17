# Penn LEAD: Penn Longitudinal Executive functioning in Adolescent Development

Reproducibility details found here: https://pennlinc.github.io/transdiagnostic_executive_function/

Penn LEAD is a longitudinal dataset consisting of clinical, cognitive, and multimodal neuroimaging data from 132 adolescents, designed to investigate **transdiagnostic executive function**.

The data descriptor paper corresponding with this repository can be found on bioRxiv: [Link](https://doi.org/10.1101/2025.11.10.687633)

The data corresponding with this repository can be found on OpenNeuro:
+ [Raw data](https://openneuro.org/datasets/ds007116)
+ [sMRIPrep derivatives](https://openneuro.org/datasets/ds007089)
+ [fMRIPrep derivatives](https://openneuro.org/datasets/ds007088)
+ [XCP-D derivatives](https://openneuro.org/datasets/ds007402)
+ [QSIPrep derivatives](https://openneuro.org/datasets/ds007090)
+ [QSIRecon derivatives](https://openneuro.org/datasets/ds007091)
+ [ASLPrep derivatives](https://openneuro.org/datasets/ds006744)


### Description of folders in repository

+ The `clinical`, `cognitive`, and `demographics` folders contain everything needed to generate summaries and figures relating to clinical phenotypic data, data from the Penn Computerized Neurocognitive Battery (CNB), and demographic information contained within the participants.tsv file in the dataset.
+ The `self_report` folder contains the scripts used to score each self-report scale included in the dataset.
+ The `curation` folder contains necessary scripts needed to curate the multimodal neuroimaging data, score the n-back task fMRI data, anonymize the scans, and summarize the raw data available. The `preprocessing` folder contains necessary scripts needed to complement preprocessing of the multimodal imaging data through BABS (Bids App Bootstrap) software, and a folder containing the YAML files that were used to run each BIDS App through BABS, as well as a script to summarize the available preprocessed data.
+ The `QC` folder contains the scripts used to concatenate and compile relevant QC information from BIDS App outputs, as well as the CSV files and figures generated from these scripts to help make QC determinations, and a script to summarize the amount of subjects and sessions that passed QC. It also contains a folder with CSV files containing lists of the scans excluded from analysis scripts for each imaging modality, as well as a set of CSV files with our final QC recommendations for each modality.
+ The `data` folder includes a list of all the subject IDs included in the dataset.
+ The `analysis` folder contains scripts needed to unzip and plot data from processed outputs for visualization. The `neuroimaging_figures` folder contains the PNG and PDF images that resulted from running these scripts.
+ The `task_contrast` folder contains all scripts and outputs from running task contrast analyses using Nilearn.
+ The `python_requirements` folder contains text files containing details about the environments used to run scripts.
+ The `cubic_org` folder contains a README for internal documentation about project organization on the cubic cluster.
