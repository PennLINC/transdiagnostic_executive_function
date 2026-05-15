# Summary of nback conversion and scoring scripts

## generate_session_map.py

This script generates a session map TSV file from the flywheel sourcedata directory by comparing the timestamp of the <sesid>.flywheel.json file in each session directory.

## check_date_match.py

This script checks if the date of the session in the session_map.tsv file output by `generate_session_map.py` matches the date of the session in the all_sessions_times.tsv in the original bids data directory (`/cbica/projects/executive_function/data/bids/EF_bids_data/`).

## check_log_missingness.py

This script gathers all participant_ids and ses_ids from the BIDS dataset and compares them to the flywheel logs directory to check for missing logs. It also optionally recovers missing logs from the BOX datadump folder - crossing checking the date of the log files against the session_map.tsv file to ensure the log file is from the correct session. It outputs a report of the missing logs and the logs that were recovered. Example usage:

```
python code/curation/cubids_curation/check_log_missingness.py \
  --logs-dir task_events_files/flywheel/EFR01/SUBJECTS/ \
  --session-map /cbica/projects/executive_function/task_events_files/session_map.tsv \
  --bids-dir data/bids/EF_bids_data_DataLad/ \
  --datadump-root /cbica/projects/executive_function/task_events_files/original_box_folders/SCANNER_TASK \
  --log-pattern *-frac2B_1.00_no1B*.log \
  --report-tsv code/curation/cubids_curation/recovery_report_APPLY_v3.tsv
```

## convert_and_score_EF_task_data.py

This script converts the EF fractal n-back logs to BIDS-compliant events and updates the sessions.tsv file with summary scores and performance metrics.
It takes as input the xml file that contains the scoring template for the task (`msmri522_2vs0_back.xml`) and the flywheel logs directory, along with the session_map.tsv file output by `generate_session_map.py`.
This script was converted from a legacy coversion and scoring script: `convert_and_score_EF_task_data.ipynb`.


## ensure_sessions_json.py

This script ensures that the sessions.json file for each subject exists and has the correct fields.
This created jsons for the 10 subjects who had no n-back and therefore did not have jsons created in the previous step.
Example usage:
```
python code/curation/cubids_curation/ensure_sessions_json.py \
  --bids-dir data/bids/EF_bids_data_DataLad/
```
