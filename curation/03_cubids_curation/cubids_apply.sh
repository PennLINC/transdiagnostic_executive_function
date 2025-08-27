#!/bin/bash
#SBATCH --job-name=cubids_apply
#SBATCH --output=/cbica/projects/executive_function/code/logs/cubids_apply_%A.out # Output log
#SBATCH --error=/cbica/projects/executive_function/code/logs/cubids_apply_%A.err  # Error log
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --time=48:00:00        # Adjust time as needed
#SBATCH --mem=64G

# Add mamba environment executables to path
source /cbica/projects/executive_function/.bash_profile
PATH=$PATH:/cbica/projects/executive_funcion/miniforge3/envs/cubids/bin/
PATH=$PATH:/cbica/projects/executive_function/miniforge3/condabin/
PATH=$PATH:/cbica/projects/executive_function/data/bids
mamba activate cubids

# Run CuBIDS apply
cd /cbica/projects/executive_function/data/bids/
/cbica/projects/executive_function/miniforge3/envs/cubids/bin/cubids apply /cbica/projects/executive_function/data/bids/EF_bids_data_DataLad /cbica/projects/executive_function/data/bids/EF_bids_data_DataLad/code/CuBIDS/v22_edited_summary.tsv /cbica/projects/executive_function/data/bids/EF_bids_data_DataLad/code/CuBIDS/v22_files.tsv v23 
