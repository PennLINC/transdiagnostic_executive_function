import os
import re
import glob
import zipfile
import numpy as np
# import datalad.api as dl


datapath = '/cbica/projects/executive_function/EF_dataset/'
fmriprep_anat_path = os.path.join(datapath,
                         'derivatives/fmriprepANAT_BABS_EF_full_project_outputs/')
MNI_path = os.path.join(fmriprep_anat_path, 'QC/T1w_space-MNI/')

# # uncomment if using datalad get from within python
# ds = dl.Dataset(datapath)

file_list = glob.glob(os.path.join(fmriprep_anat_path, 'sub-*_ses-*_fmriprep_anat-25-0-0.zip'))
file_list.sort()

for f in range(len(file_list)):
    # # uncomment if using datalad get from within python
    # ds.get(file_list[f])
    # # but instead of this ^ , I did datalad get in batches
    # # (e.g. datalad get sub-0*_xcp-0-3-0.zip)
    # # then unzip with this script, then drop

    with zipfile.ZipFile(file_list[f]) as zf:
        fileNames = zf.namelist()

    fileNames = np.array(fileNames)

    # define file types you want from fmriprep_anat outputs
    dataTypes = ['_space-MNI152NLin6Asym_res-1_desc-preproc_T1w.nii.gz',
						     ]


    wantedFiles = []
    for dataType in dataTypes:
        search = dataType + '+'
        for iFile in fileNames:
            if (re.findall(dataType, iFile)):
                wantedFiles.append(iFile)

    with zipfile.ZipFile(file_list[f], 'r') as zip_ref:
        for specFile in wantedFiles:
            zip_ref.extract(specFile, MNI_path)
        zip_ref.close()

    # # uncomment if using datalad get from within python
    # ds.drop(file_list[f])

    print('\nFiles in %s done!' % file_list[f])
   
