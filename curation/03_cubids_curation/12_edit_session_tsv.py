import os
import pandas as pd

"""
Once sessions.tsv files are created, this script makes the tsv files BIDS-compliant by renaming the 'datetime' column name in original created sessions.tsv file to 'acq_time'.
"""

# Path to the scans_tsv_temp2 directory
scans_tsv_temp2_dir = '/cbica/projects/executive_function/data/bids/scans_tsv_temp2' #CUBIC project path

# Loop through all subject directories in the scans_tsv_temp2 directory
for subject_dir in os.listdir(scans_tsv_temp2_dir):
    subject_path = os.path.join(scans_tsv_temp2_dir, subject_dir)
    
    # Check if it's a directory and if it contains a sessions.tsv file
    if os.path.isdir(subject_path):
        sessions_file = os.path.join(subject_path, 'sessions.tsv')
        
        if os.path.exists(sessions_file):
            # Load the sessions.tsv file into a pandas DataFrame
            df = pd.read_csv(sessions_file, sep='\t')
            
            # Rename 'datetime' column to 'acq_time'
            if 'datetime' in df.columns:
                df.rename(columns={'datetime': 'acq_time'}, inplace=True)
                
                # Save the updated DataFrame back to the sessions.tsv file
                df.to_csv(sessions_file, sep='\t', index=False)
                print(f"Updated 'datetime' to 'acq_time' in {sessions_file}")
