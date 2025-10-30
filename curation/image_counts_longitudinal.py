import os
from collections import defaultdict

# Define matching logic for image types
MODALITY_RULES = {
    "T1": lambda f: f.endswith("T1w.nii.gz"),
    "T2": lambda f: f.endswith("T2w.nii.gz") and "norm" not in f,
    "T2 norm": lambda f: f.endswith("T2w.nii.gz") and "norm" in f,
    "ASL": lambda f: f.endswith("asl.nii.gz"),
    "functional fMRI": lambda f: f.endswith("bold.nii.gz"),
    "diffusion": lambda f: f.endswith("dwi.nii.gz"),
}

# Define which folder to look in for each image type
MODALITY_FOLDERS = {
    "T1": "anat",
    "T2": "anat",
    "T2 norm": "anat",
    "ASL": "perf",
    "functional fMRI": "func",
    "diffusion": "dwi",
}

def search_images(base_dir, modality):
    folder_type = MODALITY_FOLDERS[modality]
    match_func = MODALITY_RULES[modality]

    participant_count = 0
    scan_count = 0  # counts sessions with at least one matching scan
    longitudinal_count = 0
    non_longitudinal_count = 0

    for participant in os.listdir(base_dir):
        if not participant.startswith("sub-"):
            continue

        participant_path = os.path.join(base_dir, participant)
        if not os.path.isdir(participant_path):
            continue

        session_hits = 0

        for session in os.listdir(participant_path):
            session_path = os.path.join(participant_path, session)
            folder_path = os.path.join(session_path, folder_type)
            if not os.path.isdir(folder_path):
                continue

            # Only count one match per session
            for file in os.listdir(folder_path):
                if match_func(file):
                    scan_count += 1
                    session_hits += 1
                    break

        if session_hits > 0:
            participant_count += 1
            if session_hits > 1:
                longitudinal_count += 1
            else:
                non_longitudinal_count += 1

    percent_longitudinal = (
        100 * longitudinal_count / (longitudinal_count + non_longitudinal_count)
        if (longitudinal_count + non_longitudinal_count) > 0 else 0
    )

    print(f"{modality} participant count: {participant_count}")
    print(f"{modality} session count: {scan_count}")
    print(f"{modality} longitudinal count: {longitudinal_count}")
    print(f"{modality} non-longitudinal count: {non_longitudinal_count}")
    print(f"{modality} percent longitudinal: {percent_longitudinal:.1f}%\n")

if __name__ == "__main__":
    BASE_DIR = "/cbica/projects/executive_function/data/bids/EF_bids_data_DataLad"
    for modality in MODALITY_RULES.keys():
        search_images(BASE_DIR, modality)

