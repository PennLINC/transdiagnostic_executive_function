#!/bin/bash
#SBATCH --job-name=nback_secondlevel_final_3_thresholded
#SBATCH --output=nback_secondlevel_final_3_thresholded_%j.out
#SBATCH --error=nback_secondlevel_final_3_thresholded_%j.err
#SBATCH --time=08:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G

eval "$(micromamba shell hook --shell bash)"
micromamba activate nilearn_glm

python /cbica/projects/executive_function/code/task_contrast/final/code/run_nback_second_level_thresholded.py
