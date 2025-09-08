import os
import re

"""
This script re-names certain files with an obliquity variant to a BIDS-valid name for these files.
"""

# Define the base directory
base_dir = "/cbica/projects/executive_function/data/bids/EF_bids_data_DataLad" #CUBIC project path

# Iterate over subjects
for subject in os.listdir(base_dir):
    subject_path = os.path.join(base_dir, subject)
    if not os.path.isdir(subject_path):
        continue  # Skip if not a directory
    
    # Iterate over sessions
    for session in os.listdir(subject_path):
        session_path = os.path.join(subject_path, session)
        fmap_path = os.path.join(session_path, "fmap")
        
        if not os.path.isdir(fmap_path):
            continue  # Skip if fmap folder doesn't exist
        
        # Iterate over files in fmap folder
        for filename in os.listdir(fmap_path):
            if "VARIANTObliquity" in filename:
                match = re.search(r'acq-VARIANTObliquity_([^_]+)_', filename)
                if match:
                    modality = match.group(1)  # Extract the part to move
                    new_filename = filename.replace(f'VARIANTObliquity_{modality}_', f'{modality}VARIANTObliquity_') #switching names of files that were in the wrong order
                    
                    # Rename the file
                    old_filepath = os.path.join(fmap_path, filename)
                    new_filepath = os.path.join(fmap_path, new_filename)
                    os.rename(old_filepath, new_filepath)
                    print(f'Renamed: {filename} -> {new_filename}')
