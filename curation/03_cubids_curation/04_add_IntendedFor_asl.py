import os
import json

# Define the base directory containing all subject folders
base_dir = '/cbica/projects/executive_function/data/bids/EF_bids_data_DataLad' #CUBIC project path

# Loop through all subject and session directories
for root, dirs, files in os.walk(base_dir):
    # Check if we're in a 'perf' folder
    if root.endswith("perf"):
        # Create dictionaries to store m0scan.json and asl.nii.gz files by their run numbers
        m0scan_files = {}
        asl_files = {}
        
        # Identify files and extract run numbers
        for file in files:
            if "run-" in file:
                if file.endswith("m0scan.json"):
                    # Extract run number from filename (e.g., run-01)
                    run = file.split("_")[2]  # Assuming consistent naming structure
                    m0scan_files[run] = file
                elif file.endswith("asl.nii.gz"):
                    # Extract run number from filename (e.g., run-01)
                    run = file.split("_")[2]  # Assuming consistent naming structure
                    asl_files[run] = file

        # Match m0scan.json files to corresponding asl.nii.gz files based on run number
        for run, m0scan_json in m0scan_files.items():
            if run in asl_files:
                asl_file = asl_files[run]
                m0scan_path = os.path.join(root, m0scan_json)
                
                # Get the relative path to the ASL file, relative to the subject directory
                subject_dir = os.path.dirname(os.path.dirname(root))  # Go up two levels to the subject directory
                asl_relative_path = os.path.relpath(os.path.join(root, asl_file), subject_dir)
                
                # Load the m0scan.json file
                with open(m0scan_path, "r") as f:
                    m0scan_data = json.load(f)
                
                # Add or update the IntendedFor field
                m0scan_data["IntendedFor"] = asl_relative_path
                
                # Save the updated JSON file
                with open(m0scan_path, "w") as f:
                    json.dump(m0scan_data, f, indent=4)
                
                print(f"Updated {m0scan_json} with IntendedFor: {asl_relative_path}")
            else:
                print(f"No matching ASL file found for {m0scan_json} (run {run}) in {root}")
