import os

"""
This script renames fmap obliquity variants - it should have occured in the CuBIDS apply stage, but ran this python script due to bug in CuBIDS.
"""

# Define base directory
base_dir = "/cbica/projects/executive_function/data/bids/EF_bids_data_DataLad"

# Define lists of subjects/sessions for each category
dwi_fmap_ap = [
    ("sub-20812", "ses-3"), ("sub-20259", "ses-3"), ("sub-19861", "ses-1"), ("sub-20188", "ses-3"),
    ("sub-20572", "ses-1"), ("sub-20976", "ses-3"), ("sub-20902", "ses-3"), ("sub-20964", "ses-1"),
    ("sub-21713", "ses-2"), ("sub-21623", "ses-2"), ("sub-21712", "ses-2"), ("sub-21567", "ses-1"),
    ("sub-21553", "ses-2"), ("sub-21539", "ses-1"), ("sub-21554", "ses-2"), ("sub-22617", "ses-2"),
    ("sub-22510", "ses-2"), ("sub-22473", "ses-2"), ("sub-22064", "ses-2"), ("sub-22045", "ses-2"),
    ("sub-22618", "ses-2"), ("sub-23582", "ses-1"), ("sub-23676", "ses-1")
]

dwi_fmap_pa = [
    ("sub-20259", "ses-3"), ("sub-20188", "ses-3"), ("sub-20812", "ses-3"), ("sub-20572", "ses-1"),
    ("sub-20976", "ses-3"), ("sub-20902", "ses-3"), ("sub-20964", "ses-1"), ("sub-21713", "ses-2"),
    ("sub-21623", "ses-2"), ("sub-21712", "ses-2"), ("sub-21567", "ses-1"), ("sub-21553", "ses-2"),
    ("sub-21539", "ses-1"), ("sub-21554", "ses-2"), ("sub-22617", "ses-2"), ("sub-22510", "ses-2"),
    ("sub-22473", "ses-2"), ("sub-22064", "ses-2"), ("sub-22045", "ses-2"), ("sub-22618", "ses-2"),
    ("sub-23582", "ses-1"), ("sub-23676", "ses-1")
]

fmri_fmap_ap = [
    ("sub-20812", "ses-3"), ("sub-20572", "ses-1"), ("sub-20303", "ses-1"), ("sub-20352", "ses-2"),
    ("sub-20259", "ses-3"), ("sub-20188", "ses-3"), ("sub-20902", "ses-3"), ("sub-20964", "ses-1"),
    ("sub-20976", "ses-3"), ("sub-21713", "ses-2"), ("sub-21623", "ses-2"), ("sub-21712", "ses-2"),
    ("sub-21554", "ses-2"), ("sub-21553", "ses-2"), ("sub-21539", "ses-1"), ("sub-21567", "ses-1"),
    ("sub-22510", "ses-2"), ("sub-22473", "ses-2"), ("sub-22064", "ses-2"), ("sub-22045", "ses-2"),
    ("sub-22617", "ses-2"), ("sub-22618", "ses-2"), ("sub-23582", "ses-1"), ("sub-23676", "ses-1")
]

fmri_fmap_pa = [
    ("sub-20812", "ses-3"), ("sub-20572", "ses-1"), ("sub-20259", "ses-3"), ("sub-20352", "ses-2"),
    ("sub-20303", "ses-1"), ("sub-20188", "ses-3"), ("sub-20902", "ses-3"), ("sub-20964", "ses-1"),
    ("sub-20976", "ses-3"), ("sub-21713", "ses-2"), ("sub-21623", "ses-2"), ("sub-21712", "ses-2"),
    ("sub-21554", "ses-2"), ("sub-21553", "ses-2"), ("sub-21539", "ses-1"), ("sub-21567", "ses-1"),
    ("sub-22510", "ses-2"), ("sub-22473", "ses-2"), ("sub-22064", "ses-2"), ("sub-22045", "ses-2"),
    ("sub-22617", "ses-2"), ("sub-22618", "ses-2"), ("sub-23582", "ses-1"), ("sub-23676", "ses-1")
]

def rename_json_files(subjects_sessions, old_pattern, new_pattern):
    for sub, ses in subjects_sessions:
        fmap_dir = os.path.join(base_dir, sub, ses, "fmap")
        
        if not os.path.exists(fmap_dir):
            print(f"Skipping {fmap_dir}, does not exist.")
            continue
        
        for file in os.listdir(fmap_dir):
            if file.endswith(".json") and old_pattern in file:
                old_path = os.path.join(fmap_dir, file)
                new_file = file.replace(old_pattern, new_pattern)
                new_path = os.path.join(fmap_dir, new_file)
                
                print(f"Renaming {old_path} -> {new_path}")
                os.rename(old_path, new_path)

# Perform renaming
rename_json_files(dwi_fmap_ap, "acq-dwi_dir-AP", "acq-VARIANTObliquity_dwi_dir-AP")
rename_json_files(dwi_fmap_pa, "acq-dwi_dir-PA", "acq-VARIANTObliquity_dwi_dir-PA")
rename_json_files(fmri_fmap_ap, "acq-fmri_dir-AP", "acq-VARIANTObliquity_fmri_dir-AP")
rename_json_files(fmri_fmap_pa, "acq-fmri_dir-PA", "acq-VARIANTObliquity_fmri_dir-PA")

