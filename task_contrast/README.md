The environment used for these scripts is the `nilearn_glm` environment, for which the python requirements can be found in `/python_requirements/nilearn_glm_requirements`

In the `/code` folder:
+ Call `run_nback_glm_single_subject.py` with `run_nback_glm_first_level.slurm` to run the first-level glm analysis.
+ Call `run_nback_second_level.py` with `run_nback_glm_second_level.slurm` to run the second-level glm analysis (unthresholded group maps).
+ Call `run_nback_second_level_thresholded.py` with `run_nback_glm_second_level_thresholded.slurm` to run the second-level glm analysis with a non-parametric permutation test producing thresholded group maps.
  
+ Run `create_group_figure.py` to create pdf forms of the second-level unthresholded results that can be used as input into Adobe Illustrator for the final figures.
+ Run `create_group_thresholded_figure.py` to create pdf forms of the second-level thresholded results that can be used as input into Adobe Illustrator for the final figures.
+ Run `create_parcellated_figures.py` to create maps (and results from PNC dataset) projected to fsLR surface and parcellated with the Schaefer 400 atlas.

The `/results` folder contains the pdf forms of second-level results that can be used as input into Illustrator for the final figures.

The `compare_EF_PNC` folder contains `neuromaps_comparison.py`, code tha tuses a spin-based permutation test to get the correlation between Penn LEAD and PNC task contrast maps.
