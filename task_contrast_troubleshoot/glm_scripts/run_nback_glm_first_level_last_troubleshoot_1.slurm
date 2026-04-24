#!/bin/bash
#SBATCH --job-name=nback_last_troubleshoot_1
#SBATCH --output=nback_last_troubleshoot_1_%A_%a.out
#SBATCH --error=nback_last_troubleshoot_1_%A_%a.err
#SBATCH --array=0-32          # 33 subjects (test)
#SBATCH --time=03:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G

# --------------------------
# LOAD ENVIRONMENT
# --------------------------

module purge
eval "$(micromamba shell hook --shell bash)"
micromamba activate nilearn_glm

# --------------------------
# SUBJECT LIST (NO COMMAS)
# --------------------------

SUBJECT_LIST=(
  19861 20139 20141 20149 20188 20214 20238 20252 20253 20258 20259
  20302 20303 20305 20328 20336 20347 20350 20352 20399 20402 20403
  20410 20427 20463 20494 20533 20572 20626 20691 20712 20721 20724
)

SUB_ID=${SUBJECT_LIST[$SLURM_ARRAY_TASK_ID]}

echo "Running first-level GLM for subject: $SUB_ID"
echo "SLURM_ARRAY_TASK_ID: $SLURM_ARRAY_TASK_ID"

# --------------------------
# RUN FIRST-LEVEL SCRIPT
# --------------------------

python /cbica/projects/executive_function/code/task_contrast/final/code/run_nback_glm_single_subject_last_troubleshoot_1.py $SUB_ID

