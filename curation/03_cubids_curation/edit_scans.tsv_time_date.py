import pandas as pd
import os
import glob

# Define the base directory
base_dir = "/cbica/projects/executive_function/data/bids/scans_tsv_temp"

# Recursively find all _scans.tsv files
tsv_files = glob.glob(os.path.join(base_dir, "sub-*/ses-*/*_scans.tsv"))

# Define the new date to set (January 1, 1800)
new_date = '1800-01-01'

for file in tsv_files:
    df = pd.read_csv(file, sep='\t')

    if 'acq_time' in df.columns:
        try:
            # Convert to datetime using ISO 8601 format handling
            df['acq_time'] = pd.to_datetime(df['acq_time'], format='ISO8601', errors='coerce')

            # Identify any rows that failed to convert
            num_failed = df['acq_time'].isna().sum()
            if num_failed > 0:
                print(f"[WARNING] {num_failed} 'acq_time' values in {file} could not be parsed.")

            # Modify the date part only, while keeping the original time
            df.loc[df['acq_time'].notna(), 'acq_time'] = df['acq_time'].dt.strftime(f'{new_date}T%H:%M:%S')

            # Save the modified file
            df.to_csv(file, sep='\t', index=False)

            print(f"[UPDATED] '{file}' has been modified and saved.")

        except Exception as e:
            print(f"[ERROR] Failed to process {file}: {e}")

    else:
        print(f"[SKIPPED] '{file}' (no 'acq_time' column).")

print("All scans.tsv files updated successfully.")

