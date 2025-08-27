import os
import pandas as pd
from datetime import datetime
import glob

# Input and output directories
base_dir = "/cbica/projects/executive_function/data/bids/EF_bids_data/"
output_dir = "/cbica/projects/executive_function/EF_dataset_figures"
output_file = os.path.join(output_dir, "scan1_acquisition_summary.tsv")

# Store each subject's earliest ses-1 acquisition time
records = []

# Iterate through subject folders
for subject in os.listdir(base_dir):
    subject_path = os.path.join(base_dir, subject)
    if os.path.isdir(subject_path) and subject.startswith("sub-"):
        sub_id = subject.replace("sub-", "")
        ses1_dir = os.path.join(subject_path, "ses-1")

        if os.path.isdir(ses1_dir):
            # Search for *_scans.tsv inside ses-1
            scan_files = glob.glob(os.path.join(ses1_dir, "*_scans.tsv"))

            if scan_files:
                scan_file = scan_files[0]
                df = pd.read_csv(scan_file, sep="\t")

                if "acq_time" in df.columns:
                    try:
                        # Parse all times and get earliest
                        acq_times = pd.to_datetime(df["acq_time"], errors="coerce").dropna()
                        if not acq_times.empty:
                            earliest = acq_times.min()
                            formatted_time = earliest.strftime("%m/%d/%Y")
                        else:
                            formatted_time = "NA"
                    except Exception:
                        formatted_time = "NA"
                else:
                    formatted_time = "NA"
            else:
                formatted_time = "NA"
        else:
            formatted_time = "NA"

        records.append({"sub": sub_id, "scan_1_time": formatted_time})

# Create DataFrame and save
summary_df = pd.DataFrame(records)
summary_df.to_csv(output_file, sep="\t", index=False)

print(f"Saved scan1 acquisition summary to: {output_file}")

