import os
import re

def rename_anat_files(bids_root):
    # Define the regex pattern to match the incorrect filenames
    pattern = re.compile(r"(sub-\d+_ses-\d+)_run-(\d+)_rec-norm_(T[12]w)\.(nii\.gz|json)")
    
    # Walk through the directory structure
    for root, _, files in os.walk(bids_root):
        for file in files:
            match = pattern.match(file)
            if match:
                subject_session, run, modality, ext = match.groups()
                
                # Create the new filename
                new_filename = f"{subject_session}_rec-norm_run-{run}_{modality}.{ext}"
                
                # Define full paths
                old_path = os.path.join(root, file)
                new_path = os.path.join(root, new_filename)
                
                # Rename the file
                print(f"Renaming: {old_path} -> {new_path}")
                os.rename(old_path, new_path)

# Set the BIDS dataset root directory
bids_root = "/cbica/projects/executive_function/data/bids/EF_bids_data_DataLad" #CUBIC project path
rename_anat_files(bids_root)
