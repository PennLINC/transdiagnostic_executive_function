import os
import shutil

"""
This script makes the sessions.tsv files BIDS-compliant by renaming the file from 'sessions.tsv' to 'sub-{id}_sessions.tsv'.
"""

# Set the root directory where all subjects are located
root_dir = '/cbica/projects/executive_function/data/bids/EF_bids_data_DataLad' #CUBIC project path

# Loop through each subject directory
for subject_dir in os.listdir(root_dir):
    subject_path = os.path.join(root_dir, subject_dir)
    
    # Check if it is a directory (subject folder)
    if os.path.isdir(subject_path) and subject_dir.startswith('sub-'):
        
        # Define the path to the sessions.tsv file
        sessions_file = os.path.join(subject_path, 'sessions.tsv')
        
        # Check if the sessions.tsv file exists
        if os.path.exists(sessions_file):
            # Create the new filename with subject ID
            new_filename = f"{subject_dir}_sessions.tsv"
            new_file_path = os.path.join(subject_path, new_filename)
            
            # Rename the sessions.tsv file
            shutil.move(sessions_file, new_file_path)
            print(f"Renamed {sessions_file} to {new_file_path}")
        else:
            print(f"No sessions.tsv found in {subject_path}")
