#!/bin/bash
#SBATCH --job-name=nback_secondlevel_beta_series
#SBATCH --output=nback_secondlevel_beta_series_%j.out
#SBATCH --error=nback_secondlevel_beta_series_%j.err
#SBATCH --time=01:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G

eval "$(micromamba shell hook --shell bash)"
micromamba activate nilearn_glm

python /cbica/projects/executive_function/code/task_contrast/final/code/run_nback_second_level_beta_series.py
