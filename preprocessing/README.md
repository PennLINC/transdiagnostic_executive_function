The environment used to run scripts in the `preprocessing` folder is the `babs` environment, for which the python requirements can be found in `/python_requirements/babs_requirements.txt`
*Note that instead of the `babs` environment, `babs2` environment (`/python_requirements/babs2_requirements.txt`), which includes an updated version of the BABS software, was used for fmriprep and XCP-D processing, as the processing had to be re-done at a later date. 

Before using BABS software (https://pennlinc-babs.readthedocs.io/en/stable/) as a wrapper around BIDS Apps, we prepared the input BIDS dataset as a DataLad dataset, prepared the containerized BIDS App
as a DataLad dataset, and prepared a configuration yaml file for the BIDS App.
+ `make_container_babs.sh` is a helper script to make a container for BIDS Apps, but it can also be done as a manual command in terminal.
+ `babs_yaml_files` contains the yaml files for each BIDS App that was run on the data.
  + The `recon_spec.yaml` file is used for QSIRecon.
+ `workflow_derived_data.py` is a script that counts the number of available subjects and sessions after preprocessing.

The following BIDS Apps were run with BABS:
+ fMRIPrep (anat-only/structural) for structural preprocessing
+ fMRIPrep for functional preprocessing
+ XCP-D for functional post-processing
+ QSIPrep for diffusion preprocessing
+ QSIRecon for diffusion post-processing
+ ASLPrep for ASL preprocessing
+ freesurfer-post to get Euler numbers added as a covariate for T1 QC

Note that MEGRE sequences for QSM were **not** preprocessed; we did not run any BIDS Apps on them through BABS.

Once BABS projects were finished running, we unzipped the output derivative files with `unzip_derivative_files.sh` to be able to upload them onto OpenNeuro.
