import os
import json
import re
from glob import glob

"""
This script adds in required fmap keys to fmap json files (B0FieldIdentifier, ParallelReductionFactorinPlane, and PartialFourierDirection).
"""

# Define the base directory
base_dir = '/cbica/projects/executive_function/data/bids/EF_bids_data_DataLad' #CUBIC project path

# Iterate over all fmap JSON files
for fmap_file in glob(os.path.join(base_dir, "sub-*", "ses-*", "fmap", "*.json")):
    try:
        # Extract file name
        file_name = os.path.basename(fmap_file)
        
        # Parse the B0FieldIdentifier from the file name
        match = re.match(r".*sub-\d+_ses-(\d+)_acq-(\w+)_dir-(\w+)_.*_epi\.json", file_name)
        if match:
            ses_id, acq, direction = match.groups()
            b0_field_identifier = f"fmap_{acq}_{direction.lower()}_ses-{ses_id}"
        else:
            print(f"Could not parse B0FieldIdentifier for file: {file_name}")
            continue
        
        # Read the JSON file
        with open(fmap_file, "r") as f:
            data = json.load(f)
        
        # Add the new fields
        data["ParallelReductionFactorInPlane"] = 1
        data["PartialFourierDirection"] = "y"
        data["B0FieldIdentifier"] = b0_field_identifier
        
        # Write back the updated JSON file
        with open(fmap_file, "w") as f:
            json.dump(data, f, indent=4)
        
        print(f"Updated file: {fmap_file}")
    
    except Exception as e:
        print(f"Error processing file {fmap_file}: {e}")
