import os
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

# Set base directory and paths
base_dir = '/cbica/projects/executive_function/EF_dataset_figures/concatenated_data'
input_path = os.path.join(base_dir, 'concat_xcpd_qc_coverage.csv')
row_outlier_path = os.path.join(base_dir, 'concat_xcpd_qc_coverage_with_row_outlier_flag.csv')
full_outlier_path = os.path.join(base_dir, 'concat_xcpd_qc_coverage_with_column_and_row_flag.csv')

# Load data
data = pd.read_csv(input_path)
brain_data = data.iloc[:, 7:-1]

# Row-wise outlier detection (detecting individuals who are outliers)
iso_row = IsolationForest(contamination='auto', random_state=42)
brain_data['row_outlier'] = iso_row.fit_predict(brain_data)

print(brain_data['row_outlier'].value_counts())

# Add row outlier flag to original dataframe
data['individual_outlier'] = brain_data['row_outlier']

# Save updated DataFrame with row outliers
data.to_csv(row_outlier_path, index=False)

# Transpose for column-wise detection (treating each region as a sample)
brain_data_t = brain_data.drop(columns='row_outlier').T
iso_col = IsolationForest(contamination='auto', random_state=42)
column_outlier_labels = iso_col.fit_predict(brain_data_t)
brain_data_t['column_outlier'] = column_outlier_labels

print(brain_data_t['column_outlier'].value_counts())

# Append column-wise outlier flags to a dictionary
column_outliers = dict(zip(brain_data_t.index, column_outlier_labels))

# Construct region_outlier_flag row for full data
region_outlier_row = []
for col in data.columns:
    if col in column_outliers:
        region_outlier_row.append(column_outliers[col])
    else:
        region_outlier_row.append(np.nan)

# Assign to data
data.loc['region_outlier_flag'] = region_outlier_row

# Save updated DataFrame with both row and column outlier flags
data.to_csv(full_outlier_path, index=True)

# Interpretation notes:
# individual_outlier =  1 b
# individual_outlier = -1 b
# region_outlier_flag =  1 b
# region_outlier_flag = -1 b
