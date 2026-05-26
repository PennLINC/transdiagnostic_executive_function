#!/bin/bash
#SBATCH --job-name=nback
#SBATCH --output=nback%A_%a.out
#SBATCH --error=nback%A_%a.err
#SBATCH --array=0-109         #110 subjects
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

#subject list includes all subjects that have nback data and passed QC
SUBJECT_LIST=(
  19861 20139 20141 20149 20188 20214 20238 20252 20253 20258 20259
  20302 20303 20305 20328 20336 20347 20350 20352 20399 20402 20403
  20410 20427 20463 20494 20533 20572 20626 20691 20712 20721 20724
  20794 20818 20823 20836 20842 20846 20849 20855 20860 20865 20866
  20902 20916 20918 20919 20923 20934 20936 20953 20961 20966 20968
  20976 20983 21023 21035 21038 21088 21095 21104 21112 21116 21118
  21139 21141 21146 21150 21154 21161 21193 21197 21224 21325 21345
  21432 21493 21514 21516 21539 21553 21554 21560 21567 21580 21623
  21712 21713 21738 21797 21827 21855 21856 22045 22064 22473 22510
  22617 22618 22653 22654 22670 22744 22797 23303 23582 23676 23698
)

SUB_ID=${SUBJECT_LIST[$SLURM_ARRAY_TASK_ID]}

echo "Running first-level GLM for subject: $SUB_ID"
echo "SLURM_ARRAY_TASK_ID: $SLURM_ARRAY_TASK_ID"

# --------------------------
# RUN FIRST-LEVEL SCRIPT
# --------------------------

python /cbica/projects/executive_function/code/task_contrast/final/code/run_nback_glm_single_subject.py $SUB_ID

