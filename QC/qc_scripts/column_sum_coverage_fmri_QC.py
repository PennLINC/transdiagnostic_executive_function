import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# File paths
input_csv = "/cbica/projects/executive_function/EF_dataset_figures/concatenated_data/concat_xcpd_qc_coverage.csv"
output_csv = "/cbica/projects/executive_function/EF_dataset_figures/concatenated_data/concat_xcpd_qc_coverage_col_sums.csv"
output_plot_dir = "/cbica/projects/executive_function/EF_dataset_figures/concatenated_data/"
output_plot_file = os.path.join(output_plot_dir, "col_sum_histogram.png")

# Metadata columns to exclude
metadata_cols = ['sub', 'ses', 'task', 'run', 'space', 'seg', 'stat', 'acq']

# Load CSV
df = pd.read_csv(input_csv)

# Identify parcel columns
parcel_cols = [col for col in df.columns if col not in metadata_cols]

# Calculate column sums: count of values < 0.5 per parcel
col_sums = (df[parcel_cols] < 0.5).sum()

# Add a new row at the bottom with these sums (metadata columns = blank, sub = 'col_sum')
col_sum_row = {col: "" for col in metadata_cols}
col_sum_row["sub"] = "col_sum"
col_sum_row.update(col_sums.to_dict())
df = pd.concat([df, pd.DataFrame([col_sum_row])], ignore_index=True)

# Save updated CSV
df.to_csv(output_csv, index=False)

# Histogram: improved binning for discrete counts
plt.figure(figsize=(10, 6))
sns.histplot(col_sums.values, bins=range(int(col_sums.min()), int(col_sums.max()) + 2),
discrete=True, color='darkorange', edgecolor='black')
plt.title("Histogram of Column Sum (< 0.5 Coverage Count per Parcel)")
plt.xlabel("Number of Rows with Parcel Value < 0.5")
plt.ylabel("Number of Parcels")
plt.tight_layout()
plt.savefig(os.path.join(output_plot_dir, "col_sum_histogram.png"))
plt.close()

# Bar plot: frequency of each unique col_sum
col_sum_counts = col_sums.value_counts().sort_index()

plt.figure(figsize=(10, 6))
sns.barplot(x=col_sum_counts.index, y=col_sum_counts.values, color='steelblue')
plt.title("Bar Plot of Column Sums (< 0.5 Coverage Count per Parcel)")
plt.xlabel("Number of Rows with Parcel Value < 0.5")
plt.ylabel("Number of Parcels")
plt.tight_layout()
plt.savefig(os.path.join(output_plot_dir, "col_sum_barplot.png"))
plt.close()

print("Script complete. Updated CSV saved to: {}".format(output_csv))
print("Histogram saved to: {}".format(output_plot_file))

