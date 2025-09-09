The environment used for scripts in the `03_cubids_curation` folder is the `cubids` environment, for which the python requirements
can be found in `/python_requirements/cubids_requirements.txt`.

The order in which the scripts in this folder should be run is below:
1. Call flywheel sync to download data onto cubic from flywheel (`01_call_fw_sync.sh`)
2. Use HeuDiConv to convert the dicom files to NIfTI files in BIDS format (relevant scripts in `02_heudiconv_conversion` folder).
   + Originally, '01' version of the conversion script and heuristic file was used for this step. However, due to an error in the original heuristic
     file, not all the data for all the subjects was converted. For affected subjects, the '02' version of the conversion script and heuristic file were
     used, and the updated data was added into the BIDS dataset. Any CuBIDS curation steps that were already run before the error was realized were repeated on the affected subjects that had to be reconverted.
4. Update, organize, clean, and correct inaccurate metadata with CuBIDS software (`03_cubids_curation).
     + Most of the scripts included in this folder are python scripts used to add or update metadata.
     + The rest of the steps were run in terminal, or manually edited (such as discussing which repeated runs of scans to delete and manually deleting them).
     + The `cubids_apply.sh` bash script allows running CuBIDS apply as a job on the cluster, as it takes a while to run.
     + It is important to `datalad save -m "..."` with a commit message after editing the metadata with CuBIDS.
5. Anonymize the scans before preprocessing (reface T1s & deface T2s) with `04_reface_anathomicals.sh`

