import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# -------------------------------
# Configuration
# -------------------------------
qc_csv = "/cbica/projects/executive_function/EF_dataset_figures/concatenated_data/concat_qsiprep_qc.csv"
row_outliers_csv = "/cbica/projects/executive_function/EF_dataset_figures/concatenated_data/row_sum_bundle_volume.csv"
plot_dir = "/cbica/projects/executive_function/EF_dataset_figures/concatenated_data"
os.makedirs(plot_dir, exist_ok=True)

# -------------------------------
# Load QC file (with bare subject/session)
# -------------------------------
df_qc = pd.read_csv(qc_csv)
df_qc = df_qc.rename(columns={'sub': 'subject', 'ses': 'session'})
df_qc = df_qc[['subject', 'session', 'mean_fd', 'raw_neighbor_corr']]

# Ensure they're strings
df_qc['subject'] = df_qc['subject'].astype(str)
df_qc['session'] = df_qc['session'].astype(str)

# -------------------------------
# Load outlier file (with BIDS-style subject/session)
# -------------------------------
df_outliers = pd.read_csv(row_outliers_csv)
df_outliers = df_outliers[['subject', 'session', 'num_row_outliers']]

# Strip "sub-" and "ses-" prefixes, then convert to string
df_outliers['subject'] = df_outliers['subject'].str.replace('sub-', '').astype(str)
df_outliers['session'] = df_outliers['session'].str.replace('ses-', '').astype(str)

# -------------------------------
# Merge on cleaned subject/session
# -------------------------------
df_merged = pd.merge(df_qc, df_outliers, on=['subject', 'session'], how='inner')
print(f"Merged rows: {len(df_merged)}")

# -------------------------------
# Plot 1: mean FD vs. number of row outliers
# -------------------------------
plt.figure(figsize=(6, 5))
sns.scatterplot(data=df_merged, x='mean_fd', y='num_row_outliers')
plt.title('Mean FD vs. Number of Row Outliers')
plt.xlabel('Mean Framewise Displacement')
plt.ylabel('Number of Bundle Outliers')
plt.tight_layout()
fd_plot_path = os.path.join(plot_dir, 'diffusion_scatter_mean_fd_vs_row_outliers.png')
plt.savefig(fd_plot_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Saved: {fd_plot_path}")

# -------------------------------
# Plot 2: Neighbor corr vs. number of row outliers
# -------------------------------
plt.figure(figsize=(6, 5))
sns.scatterplot(data=df_merged, x='raw_neighbor_corr', y='num_row_outliers')
plt.title('Neighbor Correlation vs. Number of Row Outliers')
plt.xlabel('Raw Neighbor Correlation')
plt.ylabel('Number of Bundle Outliers')
plt.tight_layout()
corr_plot_path = os.path.join(plot_dir, 'diffusion_scatter_neighbor_corr_vs_row_outliers.png')
plt.savefig(corr_plot_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Saved: {corr_plot_path}")

