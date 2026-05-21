#!/usr/bin/env python

from pathlib import Path

job_id = "15289941"
logs = sorted(Path(".").glob(f"nback_*{job_id}*.out"))

missing_events = []
excluded_subjects = []
all_na_response = []

for log in logs:
    lines = log.read_text(errors="replace").splitlines()

    subject = None
    for line in lines:
        if line.startswith("Running first-level GLM for subject:"):
            subject = line.split(":")[-1].strip()
            break

    section = None
    for line in lines:
        stripped = line.strip()

        if stripped.startswith("Sessions excluded because response_time was all n/a"):
            section = "all_na"
            continue
        elif stripped.startswith("Sessions with missing events.tsv"):
            section = "missing"
            continue
        elif stripped.startswith("Entirely excluded subject"):
            section = "excluded"
            continue
        elif stripped.startswith("Usable sessions"):
            section = None
            continue
        elif stripped.startswith("[") or stripped.startswith("Using fMRIPrep"):
            section = None

        if stripped == "None" or stripped == "":
            continue

        if section == "all_na" and stripped.startswith("sub-"):
            all_na_response.append((log.name, stripped))

        elif section == "missing" and stripped.startswith("sub-"):
            missing_events.append((log.name, stripped))

        elif section == "excluded" and stripped.startswith("sub-"):
            excluded_subjects.append((log.name, stripped))

print(f"\nChecked {len(logs)} logs with job ID {job_id}\n")

print("===================================")
print("Sessions with missing events.tsv")
print("===================================")
if missing_events:
    for log, item in missing_events:
        print(f"{log}: {item}")
else:
    print("None")

print("\n===================================")
print("Sessions where response_time was all n/a")
print("===================================")
if all_na_response:
    for log, item in all_na_response:
        print(f"{log}: {item}")
else:
    print("None")

print("\n===================================")
print("Entirely excluded subjects")
print("===================================")
if excluded_subjects:
    for log, item in excluded_subjects:
        print(f"{log}: {item}")
else:
    print("None")
    
    
