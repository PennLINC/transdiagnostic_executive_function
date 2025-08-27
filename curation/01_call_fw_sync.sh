#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=48:00:00
#SBATCH --output=/cbica/projects/executive_function/data/bids/code/sync_fw/logs/sync_fw-%A.out
#SBATCH --error=/cbica/projects/executive_function/data/bids/code/sync_fw/logs/sync_fw-%A.err

unset LD_LIBRARY_PATH # Do not use old GLIBC
/cbica/projects/executive_function/glibc-2.34/install/lib/ld-linux-x86-64.so.2 /cbica/projects/executive_function/fw/fw sync -m --include dicom fw://bbl/EFR01 /cbica/projects/executive_function/data/bids/sourcedata/
