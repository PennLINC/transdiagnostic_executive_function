import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# --- File paths ---
input_csv = "/cbica/projects/executive_function/EF_dataset_figures/concatenated_data/concat_xcpd_qc_coverage.csv" #CUBIC project path
output_csv = "/cbica/projects/executive_function/EF_dataset_figures/concatenated_data/concat_xcpd_qc_coverage_row_sums.csv" #CUBIC project path
output_dir = "/cbica/projects/executive_function/EF_dataset_figures/concatenated_data/" #CUBIC project path
output_plot_regular = os.path.join(output_dir, "row_sum_histogram_trimmed.png")
output_plot_log = os.path.join(output_dir, "row_sum_histogram_logy_trimmed.png")
output_plot_bar = os.path.join(output_dir, "row_sum_barplot.png")

# --- Metadata columns to exclude from analysis ---
metadata_cols = ['sub', 'ses', 'task', 'run', 'space', 'seg', 'stat', 'acq']

# --- Load data ---
df = pd.read_csv(input_csv)

# --- Identify parcel columns ---
parcel_cols = [col for col in df.columns if col not in metadata_cols]

# --- Compute row sum: count of parcel values < 0.5 ---
df['row_sum'] = (df[parcel_cols] < 0.5).sum(axis=1)

# --- Save updated CSV ---
df.to_csv(output_csv, index=False)

# --- Determine observed range ---
row_sum_min = df['row_sum'].min()
row_sum_max = df['row_sum'].max()
bins = range(int(row_sum_min), int(row_sum_max) + 2)

# --- Regular histogram (trimmed) ---
sns.set(style="whitegrid")
plt.figure(figsize=(10, 6))
sns.histplot(df['row_sum'], bins=bins, kde=False, color='steelblue', edgecolor='black')
plt.title("Histogram of Row Sum (< 0.5 Parcel Values)")
plt.xlabel("Number of Parcel Values < 0.5")
plt.ylabel("Frequency")
plt.tight_layout()
plt.savefig(output_plot_regular)
plt.close()

# --- Log-scaled histogram (trimmed) ---
plt.figure(figsize=(10, 6))
sns.histplot(df['row_sum'], bins=bins, kde=False, color='darkorange', edgecolor='black', log_scale=(False, True))
plt.title("Histogram of Row Sum (Log-Scaled Y-Axis)")
plt.xlabel("Number of Parcel Values < 0.5")
plt.ylabel("Log-scaled Frequency")
plt.tight_layout()
plt.savefig(output_plot_log)
plt.close()

# --- Bar plot for exact counts ---
row_sum_counts = df['row_sum'].value_counts().sort_index()
plt.figure(figsize=(10, 6))
sns.barplot(x=row_sum_counts.index, y=row_sum_counts.values, color='mediumseagreen', edgecolor='black')
plt.title("Bar Plot of Row Sum Values (< 0.5 Parcels)")
plt.xlabel("Row Sum")
plt.ylabel("Frequency")
plt.tight_layout()
plt.savefig(output_plot_bar)
plt.close()

print(f"Updated CSV saved to: {output_csv}")
print(f"Trimmed histogram saved to: {output_plot_regular}")
print(f"Log-scaled histogram saved to: {output_plot_log}")
print(f"Bar plot saved to: {output_plot_bar}")

