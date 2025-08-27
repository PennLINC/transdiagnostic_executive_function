import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# -------------------------------
# Configuration
# -------------------------------
input_csv = "/cbica/projects/executive_function/EF_dataset_figures/concatenated_data/concatenated_bundle_volume.csv"
output_csv = "/cbica/projects/executive_function/EF_dataset_figures/concatenated_data/column_sum_bundle_volume.csv"
plot_path = "/cbica/projects/executive_function/EF_dataset_figures/concatenated_data/column_bundle_outlier_distribution.png"

# -------------------------------
# Load and define columns
# -------------------------------
df = pd.read_csv(input_csv)
meta_cols = ['subject', 'session']
exclude = meta_cols + ['total_volume_all_bundles', 'mean_bundle_volume']
volume_cols = [col for col in df.columns if col not in exclude]

# -------------------------------
# Compute statistics
# -------------------------------
mean_row = df[volume_cols].mean(axis=0)
std_row = df[volume_cols].std(axis=0)
upper_thresh = mean_row + 3 * std_row
lower_thresh = mean_row - 3 * std_row

# -------------------------------
# Create outlier matrix (two-tailed)
# -------------------------------
outlier_df = df.copy()
for col in volume_cols:
    outlier_df[col] = ((df[col] >= upper_thresh[col]) | (df[col] <= lower_thresh[col])).astype(int)

# Create summary rows (leave meta columns blank)
mean_row_full = {col: mean_row[col] if col in volume_cols else "" for col in df.columns}
outlier_count_row = {col: outlier_df[col].sum() if col in volume_cols else "" for col in df.columns}

# Append summary rows
outlier_df.loc['mean_bundle_column_volume'] = pd.Series(mean_row_full)
outlier_df.loc['num_column_outliers'] = pd.Series(outlier_count_row)

# -------------------------------
# Save CSV
# -------------------------------
outlier_df.to_csv(output_csv, index=False)
print(f"Saved outlier matrix with metadata to: {output_csv}")

# -------------------------------
# Plot distribution of num_column_outliers
# -------------------------------
num_outliers_series = pd.Series(outlier_count_row)
num_outliers_series = pd.to_numeric(num_outliers_series, errors='coerce').dropna()

plt.ion()
sns.displot(num_outliers_series, kde=True, bins=20)
plt.title('Outlier Count per Bundle (greater or less than 3 SD from Mean)')
plt.xlabel('Number of Outliers')
plt.ylabel('Bundle Count')
plt.tight_layout()
plt.savefig(plot_path, bbox_inches='tight', dpi=300, transparent=True)
plt.close()

print(f"Saved outlier count distribution plot to: {plot_path}")

