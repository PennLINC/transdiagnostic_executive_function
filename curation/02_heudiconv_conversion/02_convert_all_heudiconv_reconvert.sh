#!/bin/bash
#SBATCH --job-name=heudiconv_conversion_reconvert 
#SBATCH --array=0-20   
#SBATCH --time=24:00:00                  
#SBATCH --cpus-per-task=4                
#SBATCH --mem=8G                         
#SBATCH --output=/cbica/projects/executive_function/code/heudiconv/logs/heudiconv_%A_%a.out # Output log
#SBATCH --error=/cbica/projects/executive_function/code/heudiconv/logs/heudiconv_%A_%a.err  # Error log

# Define paths
base_dir="/cbica/projects/executive_function/data/bids/sourcedata/EFR01" #CUBIC project path to data downloaded from Flywheel
output_dir="/cbica/projects/executive_function/data/bids/EF_bids_data_reconverted" #CUBIC project path

# Step 1: Get all subject IDs
subjects=("20124" "20125" "20141" "20236" "20333" "20335" "20336" "20347" "20350" "20305" "19861" "20139" "20214" "20259" "20410" "20253" "20399" "20188" "20252" "20352" "20149")

# Step 2: Select the current subject based on the SLURM array task ID
subID=${subjects[${SLURM_ARRAY_TASK_ID}]}


# Step 3: Find all session directories for the current subject
mapfile -t session_dirs < <(find ${base_dir}/SUBJECTS/${subID}/SESSIONS/* -maxdepth 0 -type d | sort -t '/' -k11n)


# Step 4: Process each session directory with dynamic session renaming
session_counter=1  # Initialize session counter
for session_dir in "${session_dirs[@]}"; do
    # Extract the numeric session name (e.g., 1153)
    session=$(basename "$session_dir")

    # Dynamically create the new session ID (e.g., ses-1, ses-2)
    #new_session_id=$(printf "ses-%d" "$session_counter")
    new_session_id="$session_counter"

    echo "Processing session ${session} for subject ${subID} in directory ${session_dir} as ${new_session_id}"  # Debugging info


    # Run heudiconv with dynamic session renaming
    heudiconv \
        -f /cbica/projects/executive_function/dropbox/heuristic_cubic_2_reconvert.py \  # corresponds to 02_heuristic_reconvert.py in github folder
        -o "$output_dir" \
        --files $session_dir/ACQUISITIONS/*/FILES/*/*.dcm \
        -s "$subID" \
        -ss "$new_session_id" \
        --bids 

    # Increment session counter
    session_counter=$((session_counter + 1))
done