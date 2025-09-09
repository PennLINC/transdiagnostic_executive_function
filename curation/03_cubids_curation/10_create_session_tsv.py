import os
import pandas as pd
from datetime import datetime, timedelta

"""
This script creates session.tsv files for each subject. It anonymizes acquisition time using information from scans.tsv files in a temporary non-DataLad tracked dataset (to avoid sharing PHI), while still maintaining accurate relative times in between sessions. 
Session 1 for each subject is set to the 15th of the original month in 1800. Time is rounded to the nearest hour.
Subsequent sessions are adjusted accordingly such that the distance between acquisition times for each session are still accurate.
"""

# Path to the scans_tsv_temp2 directory
base_dir = "/cbica/projects/executive_function/data/bids/scans_tsv_temp2" #CUBIC project path

# Function to round time to the nearest hour
def round_to_nearest_hour(dt):
    if dt.minute >= 30:
        dt += timedelta(hours=1)
    return dt.replace(minute=0, second=0, microsecond=0)

# Iterate through each subject folder
for subject in os.listdir(base_dir):
    subject_path = os.path.join(base_dir, subject)
    if os.path.isdir(subject_path) and subject.startswith("sub-"):
        session_times = []

        # Iterate through each session folder
        for session in sorted(os.listdir(subject_path)):
            session_path = os.path.join(subject_path, session)
            if os.path.isdir(session_path) and session.startswith("ses-"):
                scans_file = os.path.join(session_path, f"{subject}_{session}_scans.tsv")

                if os.path.exists(scans_file):
                    scans_df = pd.read_csv(scans_file, sep="\t")
                    
                    # Get the first scan's acquisition time
                    first_scan_time = pd.to_datetime(scans_df["acq_time"].min())
                    session_times.append((session, first_scan_time))

        # Process times: set ses-1 to 15th of the original month in 1800, subsequent sessions adjusted accordingly
        if session_times:
            base_time = session_times[0][1]
            adjusted_sessions = []

            for i, (session, original_time) in enumerate(session_times):
                # Calculate total month and day offset
                year_diff = original_time.year - base_time.year
                month_diff = original_time.month - base_time.month + (year_diff * 12)
                day_diff = (original_time - base_time.replace(
                    year=original_time.year, month=original_time.month, day=base_time.day
                )).days

                # Compute new year and month based on offset
                new_year = 1800 + (base_time.month - 1 + month_diff) // 12
                new_month = (base_time.month - 1 + month_diff) % 12 + 1

                # Set new date and round time
                new_date = datetime(new_year, new_month, 15) + timedelta(days=day_diff)
                rounded_time = round_to_nearest_hour(original_time)
                adjusted_datetime = new_date.replace(hour=rounded_time.hour, minute=0, second=0)
                adjusted_sessions.append({"session_id": session, "datetime": adjusted_datetime.strftime("%Y-%m-%dT%H:00:00")})

            # Create and save sessions.tsv
            sessions_df = pd.DataFrame(adjusted_sessions)
            output_file = os.path.join(subject_path, "sessions.tsv")
            sessions_df.to_csv(output_file, sep="\t", index=False)
            print(f"Generated {output_file}")
