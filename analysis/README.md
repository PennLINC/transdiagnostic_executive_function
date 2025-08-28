The environment used for most of the scripts in the `analysis` folder is the `babs` environment, for which the python requirements can be found
in `/python_requirements/babs_requirements.txt`.
The `visualize_afq_bundles.py` script is run locally with the `dipy` environment, for which the python requirements can be found in `/python_requirements/dipy_requirements.txt'.
+ Note that this code will not work for file names with a VARIANT in the acquisition field. As such, when copying over the files from preprocessing outputs to the local folder
+ to run this script, manually change the names if there is a variant in the acquisition field. Instructions for running this script are found commented at the top of the script.

The scripts in this folder include:
+ 01_unzip: Files used to unzip files from preprocessing ouputs that are later used for QC concatenation scripts (`/QC/qc_scripts`) or plotting group average scripts (`/analysis/02_plot`).
  Some of the files names are identical with a '_2', '_3', etc. appended if certain outputs were initially unzipped from a preprocessing output folder,
  but later more files from the same preprocessing output folder needed to be unzipped.
  + As noted in comments in individual scripts, before running the code the appropriate files must be retrieved through 'datalad get' and subsequently 'datalad drop' to drop the files once unzipped.
    The commented sections of code can be used instead of using datalad manually.
