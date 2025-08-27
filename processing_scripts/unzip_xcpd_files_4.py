import os
import re
import glob
import zipfile
import numpy as np
# import datalad.api as dl


datapath = '/cbica/projects/executive_function/EF_dataset/'
xcpd_path = os.path.join(datapath,
                         'derivatives/xcpd_BABS_EF_full_project_outputs/')

# # uncomment if using datalad get from within python
# ds = dl.Dataset(datapath)

file_list = glob.glob(os.path.join(xcpd_path, 'sub-*_ses-*_xcpd-0-10-7.zip'))
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

    # define file types you want from xcpd outputs
    dataTypes = ['_seg-4S1056Parcels_stat-pearsoncorrelation_relmat.tsv']

    wantedFiles = []
    for dataType in dataTypes:
        search = dataType + '+'
        for iFile in fileNames:
            if (re.findall(dataType, iFile)):
                wantedFiles.append(iFile)

    with zipfile.ZipFile(file_list[f], 'r') as zip_ref:
        for specFile in wantedFiles:
            zip_ref.extract(specFile, xcpd_path)
        zip_ref.close()

    # # uncomment if using datalad get from within python
    # ds.drop(file_list[f])

    print('\nFiles in %s done!' % file_list[f])
