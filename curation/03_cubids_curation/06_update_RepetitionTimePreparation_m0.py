import os
import glob
import json

"""
This script explicitly sets RepetitionTimePreparation to 5 for M0 scan json files after consultation with team for correct value.
"""

# Base directory containing the dataset
base_dir = "/cbica/projects/executive_function/data/bids/EF_bids_data_DataLad" #CUBIC project path

# Pattern to find all m0scan.json files
file_pattern = os.path.join(base_dir, "sub-*/ses-*/perf/*m0scan.json")

# Iterate over all matching m0scan.json files
for file_path in glob.glob(file_pattern):
    try:
        # Open and load the JSON file
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
        
        # Update the "RepetitionTimePreparation" field
        data["RepetitionTimePreparation"] = 5
        
        # Write the updated data back to the JSON file
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        
        print(f"Updated {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
