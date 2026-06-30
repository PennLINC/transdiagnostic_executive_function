# Cubic Organization: /cbica/projects/executive_function
*** denotes an especially important directory

```text
/cbica/projects/executive_function/
    |- apptainer/                         # Apptainer datasets containing .sif files for each BIDS App used in preprocessing
    |- apptainer-datasets/                # DataLad dataset versions of containerized BIDS Apps; used to create new BABS projects

    |- code/
        |- phenotype_analysis/            # Code for CNB, clinical, diagnostic, and demographic analyses
            |- clinical/                  # Code, data, and figures related to clinical diagnostic data
            |- CNB/                       # Code and data related to CNB tasks
            |_ participant_demographics/  # Code and data related to participant demographic information

        |- heudiconv/                     # Scripts for converting raw neuroimaging data to BIDS using heudiconv
        |- count_longitudinal_sessions/   # Scripts summarizing imaging session counts and longitudinal scan intervals
        |- flywheel/                      # Scripts for downloading original raw data from Flywheel to Cubic

        |- curation/ ***                  # Scripts for BIDS, CuBIDS, and BABS curation
            |- babs_curation/             # Scripts needed for BABS preprocessing
            |_ cubids_curation/           # Python scripts for metadata edits suggested by CuBIDS

        |- image_processing/ ***          # Scripts for preparing processing outputs for QC and analysis
            |- QC/                        # Scripts to concatenate QC data into usable files
            |_ unzip/                     # Scripts to unzip processing outputs needed for QC, analysis, and figures

        |- T1_QC/                         # Scripts for creating T1 QC slices for manual ratings

        |_ task_contrast/
            |_ final/                     # Final task contrast analysis directory
                |- code/ ***              # Scripts for first/second-level GLMs, figures, tables, time series, logs, and performance summaries
                    |_ qc_outputs/        # Outputs from nback attention QC scripts

                |- behavioral/            # Summary TSV files of task performance and TRs per condition
                |- figures/  ***          # Final manuscript figures from task contrast analyses
                |- task_contrast_exclusions.csv
                |                         # Sessions excluded from group task contrast maps
                |- task_contrast_PNC/     # PNC task contrast data used for comparison with EF task contrast data
                |- compare_EF_PNC/ ***    # Scripts and figures comparing EF and PNC task contrast data

                |_ results_final_3_edited/ ***
                    |- first-level/
                        |- nback-nortdur/ # Subject-level first-level GLM results without RTDur model
                        |_ nback-rtdur/   # Subject-level first-level GLM results with RTDur model

                    |_ second-level/
                        |- nback-nortdur/
                            |- group-twoBack/               # 2-back > implicit baseline
                            |- group-twoBackMinusZeroBack/  # 2-back > 0-back
                            |_ group-zeroBack/              # 0-back > implicit baseline

                        |_ nback-rtdur/
                            |- group-twoBack/               # 2-back > implicit baseline
                            |- group-twoBackMinusZeroBack/  # 2-back > 0-back
                            |_ group-zeroBack/              # 0-back > implicit baseline

    |- data/
        |_ bids/
            |- ds007116/                  # OpenNeuro upload helper dataset
            |- git-annex-remote-openneuro/
            |                             # Helper for uploading BIDS files to OpenNeuro
            |- EF_bids_data/              # BIDS-formatted neuroimaging data; not DataLad-tracked; contains non-shareable information
            |- EF_bids_data_reconverted/  # Reconverted BIDS data after correcting the heuristic file
            |- EF_bids_data_DataLad/ ***  # Main maintained BIDS DataLad dataset used for processing and analysis
            |- participants_scanned.csv   # Tracks participant IDs and number of scanned sessions
            |- Exemplar_Dataset/          # Exemplar dataset for CuBIDS
            |- original_scans_tsv/        # Original scans.tsv files with non-DataLad-tracked fields such as acquisition time
            |- sourcedata/ ***
                |_ EFR01/                 # Original raw, non-BIDS neuroimaging data downloaded from Flywheel
            |_ old_datalad_ds_to_remove/  # Old DataLad datasets pending removal due to permissions issues

    |- Data_Management.txt                # Details of the Cubic project
    |- dropbox/                           # Transfer location for files copied from local computer to Cubic

    |- EF_dataset/ ***                    # Main dataset directory for BABS, derivatives, and QC inputs
        |- braindr/                       # Axial and sagittal PNG slices used for manual T1 ratings
        |- code/                          # BABS configuration files for each modality/BIDS App
        |_ derivatives/                   # Full BABS projects and zipped/unzipped outputs for OpenNeuro

    |- EF_dataset_figures/ ***            # QC summaries, analysis outputs, and manuscript figure files
        |- concatenated_data/             # CSV, PDF, and PNG QC metric files for each modality
        |- figures/
            |- aslprep_figures/
            |- atlas_figure/
            |- fmriprep_figures/
            |- qsi_figures/               # Scalar data only; bundle data was run locally
            |_ xcpd_group_maps/
        |_ processing_scripts/            # Scripts for summaries, analyses, figures, and scan exclusion lists

    |- mamba/                             # Environment setup files
    |- matlab/                            # MATLAB setup files
    |- miniforge3/                        # Miniforge installation/environment files
    |- not_github_or_local/               # Files stored here & not published to github or on local computer
    |- python_requirements/               # Python requirements files for different environments

    |- software/                          # Downloaded software needed for the project
        |_ misc_env_software_downloads/   # Additional environment/software downloads

    |- task_contrast_openneuro_edited/    # Final task contrast derivatives prepared for OpenNeuro upload
    |- task_events_files/                 # Original n-back task files from the MRI scanner
    |- templateflow/                      # Standardized neuroimaging templates used by processing and analysis tools

    |- neuromaps-data/                    # Downloaded neuromaps data
    |- nnt-data/                          # Downloaded NetNeuroTools data

    |- RAW/                               # Raw DICOM upload directory for CBICA PACS; not relevant to this project but retained
    |- mebold_trt/                        # Separate multi-echo/single-echo data descriptor project
    |_ tien/                              # Workshop project code using the EF dataset
```
