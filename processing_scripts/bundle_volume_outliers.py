import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# -------------------------------
# Configuration
# -------------------------------
csv_path = "/cbica/projects/executive_function/EF_dataset_figures/concatenated_data/concatenated_bundle_volume.csv"
plot_dir = "/cbica/projects/executive_function/EF_dataset_figures/concatenated_data/bundle_plots"
os.makedirs(plot_dir, exist_ok=True)

# -------------------------------
# Load CSV
# -------------------------------
df = pd.read_csv(csv_path)

# Identify bundle columns only
exclude_cols = ['subject', 'session', 'total_volume_all_bundles', 'mean_bundle_volume']
bundle_cols = [col for col in df.columns if col.startswith("total_volume_mm3_") and col not in exclude_cols]

print(f"Found {len(bundle_cols)} bundle columns...")

# -------------------------------
# Generate plots
# -------------------------------
for col in bundle_cols:
    try:
        # Sanitize filename (remove prefix, keep only bundle name)
        bundle_name = col.replace("total_volume_mm3_", "")
        fname = f"{bundle_name}.png"
        fpath = os.path.join(plot_dir, fname)

        # Plot
        plt.figure(figsize=(8, 5))
        sns.histplot(df[col].astype(float), kde=True, bins=20)
        plt.title(f'Volume Distribution: {bundle_name}')
        plt.xlabel('Volume (mmB3)')
        plt.ylabel('Frequency')
        plt.tight_layout()
        plt.savefig(fpath, bbox_inches='tight', dpi=300, transparent=True)
        plt.close()

        print(f"Saved: {fpath}")

    except Exception as e:
        print(f"Failed to plot {col}: {e}")

