import os
import json
from glob import glob

# Define the base directory
base_dir = "/cbica/projects/executive_function/data/bids/EF_bids_data_DataLad" #CUBIC project path

# Dry run: set to True to preview changes without saving
dry_run = False

# Iterate over all dwi JSON files
for dwi_file in glob(os.path.join(base_dir, "sub-*", "ses-*", "dwi", "*_dwi.json")):
    try:
        # Read the JSON file
        with open(dwi_file, "r") as f:
            data = json.load(f)
        
        # Check if PartialFourierDirection is already set
        if data.get("PartialFourierDirection") == "y":
            print(f"PartialFourierDirection already set for {dwi_file}. Skipping.")
            continue
        
        # Add PartialFourierDirection field
        proposed_change = {"PartialFourierDirection": "y"} 
        
        # Show proposed changes
        print(f"\nFile: {dwi_file}")
        print("Proposed changes:")
        print(json.dumps(proposed_change, indent=4))
        
        # If not in dry run mode, apply the change
        if not dry_run:
            data.update(proposed_change)
            with open(dwi_file, "w") as f:
                json.dump(data, f, indent=4)
            print("File updated.")

    except Exception as e:
        print(f"Error processing file {dwi_file}: {e}")
