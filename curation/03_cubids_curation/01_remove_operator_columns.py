import os
import pandas as pd

# Define the root directory for your dataset
root_dir = "/cbica/projects/executive_function/data/bids/EF_bids_data_DataLad" #CUBIC project path


# Walk through the directory to find all scans.tsv files
for dirpath, dirnames, filenames in os.walk(root_dir):
    for file in filenames:
        if file.endswith("scans.tsv"):
            file_path = os.path.join(dirpath, file)
            print(f"Processing: {file_path}")
            
            # Load the TSV file into a DataFrame
            try:
                df = pd.read_csv(file_path, sep="\t")
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue
            
            # Check if 'operator' column exists and remove it
            if "operator" in df.columns:
                df = df.drop(columns=["operator"])
                print(f"Removed 'operator' column from {file_path}")
                
                # Save the updated DataFrame back to the file
                try:
                    df.to_csv(file_path, sep="\t", index=False)
                    print(f"Updated {file_path}")
                except Exception as e:
                    print(f"Error writing {file_path}: {e}")
            else:
                print(f"No 'operator' column found in {file_path}")
