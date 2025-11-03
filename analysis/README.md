The environment used for most of the scripts in the `analysis` folder is the `babs` environment, for which the python requirements can be found
in `/python_requirements/babs_requirements.txt`.
<br>The `visualize_afq_bundles.py` script is run locally with the `dipy` environment, for which the python requirements can be found in `/python_requirements/dipy_requirements.txt`.
+ Note that this code will not work for file names with a VARIANT in the acquisition field. As such, when copying over the files from preprocessing outputs to the local folder to run this script, manually change the names if there is a variant in the acquisition field. Instructions for running this script are found commented at the top of the script.


The scripts in this folder include:
+ `01_unzip`: Files used to unzip files from preprocessing ouputs that are later used for QC concatenation scripts (`/QC/qc_scripts`) or plotting group average scripts (`/analysis/02_plot`).
  Some of the files names are identical with a '_2', '_3', etc. appended if certain outputs were initially unzipped from a preprocessing output folder,
  but later more files from the same preprocessing output folder needed to be unzipped.
  + As noted in comments in individual scripts, before running the code the appropriate files must be retrieved through 'datalad get' and subsequently 'datalad drop' to drop the files once unzipped.
    The commented sections of code can be used instead of using datalad manually.
  + In some scripts, the full derivatives were unzipped for upload to OpenNeuro before running, so the unzipped folders were used in 02_plot instead of using the scripts in 01_unzip.

+ `02_plot`: Scripts used to create plots used in the manuscript and saved in `neuroimaging_folders`
    + `plot_asl_cbf_maps.py` is used to create ASL CBF maps for figure 9 in the manuscript
    + `plot_corrmat_nback.py` is used to create the n-back task correlation matrix for figure 6 in the manuscript
    + `plot_corrmat_rest_run.py` is used to create the resting-state correlation matrix for figure 6 in the manuscript
    + `plot_qsi_scalar_maps_1.py`, `plot_qsi_scalar_maps_2.py`, `plot_qsi_scalar_maps_3.py`, and `plot_qsi_scalar_maps_4.py` are used to create the scalar maps for DWI data for figure 7 in the manuscript
    + `plot_surfaces.ipynb` is used to plot ALFF and ReHO for figure 6 in the manuscript
    + `visualize_afq_bundles.py` is used to plot the individual white matter tracts for a few example subjects
