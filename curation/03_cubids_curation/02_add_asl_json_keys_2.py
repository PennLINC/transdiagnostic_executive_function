import os
import json

"""
This script adds in additional required json keys into ASL and M0 scan json files that were originally missing.
"""

# Define the root directory where your BIDS dataset is located
bids_root = '/cbica/projects/executive_function/data/bids/EF_bids_data_DataLad' #CUBIC project path

# Define the fields to add and update for ASL JSON files
asl_update_fields = {
    "BackgroundSuppression": True,
    "LabelingDuration": 1.5,
    "M0Type": "Separate"
}

# Function to update the JSON sidecar with the desired fields
def update_asl_json_sidecar(file_path, fields):
    try:
        # Open and load the existing JSON sidecar
        with open(file_path, 'r') as json_file:
            json_data = json.load(json_file)
        
        # Delete the old 'Background Suppression' key if it exists
        if 'Background Suppression' in json_data:
            del json_data['Background Suppression']
        
        # Add the new fields to the JSON data
        json_data.update(fields)
        
        # Write the updated JSON data back to the file
        with open(file_path, 'w') as json_file:
            json.dump(json_data, json_file, indent=4)
        
        print(f"Updated: {file_path}")
    
    except Exception as e:
        print(f"Error updating {file_path}: {e}")

# Loop through the subjects and sessions to find ASL JSON files
for subject_dir in os.listdir(bids_root):
    subject_path = os.path.join(bids_root, subject_dir)
    if os.path.isdir(subject_path) and subject_dir.startswith('sub-'):
        for session_dir in os.listdir(subject_path):
            session_path = os.path.join(subject_path, session_dir)
            if os.path.isdir(session_path) and session_dir.startswith('ses-'):
                # Look for perf folder
                perf_path = os.path.join(session_path, 'perf')
                if os.path.isdir(perf_path):
                    for file_name in os.listdir(perf_path):
                        file_path = os.path.join(perf_path, file_name)
                        if file_name.endswith('asl.json'):
                            # Update ASL JSON sidecar with new fields
                            update_asl_json_sidecar(file_path, asl_update_fields)
