The environment used to run scripts in the `preprocessing` folder is the `babs` environment, for which the python requirements can be found in `/python_requirements/babs_requirements.txt`

Before using BABS software () as a wrapper around BIDS Apps, we prepared the input BIDS dataset as a DataLad dataset, prepared the containerized BIDS App
as a DataLad dataset, and prepared a configuration yaml file for the BIDS App.
+ `make_container_babs.sh` is a helper script to make a container for BIDS Apps, but it can also be done as a manual command in terminal.
+ `babs_yaml_files` contains the yaml files for each BIDS App that was run on the data.
  + The `recon_spec.yaml` file is used for QSIRecon.

The following BIDS Apps were run with BABS:
+ fMRIPrep (anat-only/structural) for structural preprocessing
+ fMRIPrep for functional preprocessing
+ XCP-D for functional post-processing
+ QSIPrep for diffusion preprocessing
+ QSIRecon for diffusion post-processing
+ ASLPrep for ASL preprocessing
+ freesurfer-post to get Euler numbers added as a covariate for T1 QC

Note that MEGRE sequences for QSM were **not** preprocessed; we did not run any BIDS Apps on them through BABS.
