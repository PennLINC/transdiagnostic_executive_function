The environment used for these scripts is the `nilearn_glm` environment, for which the python requirements can be found in `/python_requirements/nilearn_glm_requirements`

In the `/code` folder:
+ Call `run_nback_glm_single_subject.py` with `run_nback_glm_first_level.slurm` to run the first-level glm analysis.
+ Call `run_nback_second_level.py` with `run_nback_glm_second_level.slurm` to run the second-level glm analysis.
+ Run `create_group_figure.py` to create pdf forms of the second-level results that can be used as input into Indesign for the final figures.

The `/results` folder contains the pdf forms of second-level results that can be used as input into Indesign for the final figures.
