from glob import glob
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

if __name__ == "__main__":
    # Load parcel dseg info
    dseg_file = (
        "/cbica/projects/executive_function/EF_dataset/derivatives/xcpd_BABS_EF_full_project_outputs/xcpd/atlases/atlas-4S1056Parcels/" #CUBIC project path
        "atlas-4S1056Parcels_dseg.tsv"
    )
    dseg_df = pd.read_table(dseg_file)

    atlas_mapper = {
        "CIT168Subcortical": "Subcortical",
        "ThalamusHCP": "Thalamus",
        "SubcorticalHCP": "Subcortical",
    }
    network_labels = dseg_df["network_label"].fillna(dseg_df["atlas_name"]).tolist()
    network_labels = [atlas_mapper.get(net, net) for net in network_labels]

    # Determine order of nodes while retaining original order of networks
    unique_labels = []
    for label in network_labels:
        if label not in unique_labels:
            unique_labels.append(label)

    mapper = {label: f"{i:03d}_{label}" for i, label in enumerate(unique_labels)}
    mapped_network_labels = [mapper[label] for label in network_labels]
    community_order = np.argsort(mapped_network_labels)

    # Get the community name associated with each network
    labels = np.array(network_labels)[community_order]
    unique_labels = []
    for label in labels:
        if label not in unique_labels:
            unique_labels.append(label)

    # Find the locations for the community-separating lines
    break_idx = [0]
    end_idx = None
    for label in unique_labels:
        start_idx = np.where(labels == label)[0][0]
        if end_idx:
            break_idx.append(np.nanmean([start_idx, end_idx]))
        end_idx = np.where(labels == label)[0][-1]
    break_idx.append(len(labels))
    break_idx = np.array(break_idx)

    # Label positions
    label_idx = np.nanmean(np.vstack((break_idx[1:], break_idx[:-1])), axis=0)

    # Find correlation matrices
    corrmats = sorted(
        glob(
            "/cbica/projects/executive_function/EF_dataset/derivatives/xcpd_BABS_EF_full_project_outputs/xcpd/sub-*/ses-*/func/"
            "*seg-4S1056Parcels_stat-pearsoncorrelation_relmat.tsv"
        )
    )

    for task in ["rest_run-03"]:
        # --- Exclude scans based on CSV ---
        excluded_scans = pd.read_csv(
            "/cbica/projects/executive_function/EF_dataset_figures/processing_scripts/excluded_scans_corrmat.csv"
        )
        excluded_scans = set(excluded_scans["excluded_scans"].astype(str).str.strip())
        print("First 5 excluded scan IDs:", list(excluded_scans)[:5])

        # --- Exclude regions based on CSV ---
        excluded_regions_df = pd.read_csv(
            "/cbica/projects/executive_function/EF_dataset_figures/processing_scripts/excluded_regions_corrmat.csv"
        )
        excluded_regions = set(excluded_regions_df["excluded_regions"].astype(str).str.strip())

        # Get region label index positions
        region_labels = dseg_df["label"].tolist()
        exclude_indices = [i for i, name in enumerate(region_labels) if name in excluded_regions]

        # --- Count total before filtering ---
        rest_run_03_all = [cm for cm in corrmats if "task-rest_run-03" in cm]
        print(f"Total rest_run_03 scans found: {len(rest_run_03_all)}")

        # --- Filter correlation matrices ---
        selected_corrmats = [
            cm for cm in rest_run_03_all 
            if not any(f"/{sub}/" in cm or f"/{sub}_" in cm for sub in excluded_scans)
        ]
        print(f"Included scans after exclusion: {len(selected_corrmats)}")

        # --- Load matrices ---
        arrs = [pd.read_table(cm, index_col="Node").to_numpy() for cm in selected_corrmats]
        arr_3d = np.dstack(arrs)
        arr_3d = np.clip(arr_3d, -0.999999, 0.999999)
        print(f"Correlation array shape: {arr_3d.shape}")

        arr_3d_z = np.arctanh(arr_3d)

        # --- Compute mean ---
        mean_arr_z = np.nanmean(arr_3d_z, axis=2)
        mean_arr_z = mean_arr_z[community_order, :][:, community_order]
        np.fill_diagonal(mean_arr_z, 0)
        mean_arr_r = np.tanh(mean_arr_z)

        # Remap excluded region indices through community_order
        exclude_indices_reordered = [
            np.where(community_order == idx)[0][0]
            for idx in exclude_indices
            if idx in community_order
        ]
        mean_arr_r[exclude_indices_reordered, :] = np.nan
        mean_arr_r[:, exclude_indices_reordered] = np.nan

        # --- Plot mean matrix ---
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.set_facecolor("white")
        cmap = mpl.cm.get_cmap("seismic").copy()
        cmap.set_bad(color="none")  # Transparent for NaN
        img = ax.imshow(mean_arr_r, cmap=cmap, vmin=-1, vmax=1)
        for idx in break_idx[1:-1]:
            ax.axvline(idx, color="black")
            ax.axhline(idx, color="black")
        ax.set_yticks(label_idx)
        ax.set_xticks(label_idx)
        ax.set_yticklabels(unique_labels)
        ax.set_xticklabels(unique_labels, rotation=90)
        fig.tight_layout()
        fig.savefig(f"/cbica/projects/executive_function/EF_dataset_figures/figures/fmriprep_figures/XCPD_task-{task}_Mean.png")
        plt.close()

        # --- Compute SD ---
        sd_arr_z = np.nanstd(arr_3d_z, axis=2)
        sd_arr_z = sd_arr_z[community_order, :][:, community_order]
        np.fill_diagonal(sd_arr_z, 0)
        sd_arr_r = np.tanh(sd_arr_z)
        sd_arr_r[exclude_indices_reordered, :] = np.nan
        sd_arr_r[:, exclude_indices_reordered] = np.nan

        # --- Plot SD matrix ---
        vmax1 = 0.6
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.set_facecolor("white")
        cmap_sd = mpl.cm.get_cmap("Reds").copy()
        cmap_sd.set_bad(color="none")  # Transparent for NaN
        img = ax.imshow(sd_arr_r, cmap=cmap_sd, vmin=0, vmax=vmax1)
        for idx in break_idx[1:-1]:
            ax.axvline(idx, color="black")
            ax.axhline(idx, color="black")
        ax.set_yticks(label_idx)
        ax.set_xticks(label_idx)
        ax.set_yticklabels(unique_labels)
        ax.set_xticklabels(unique_labels, rotation=90)
        fig.tight_layout()
        fig.savefig(f"/cbica/projects/executive_function/EF_dataset_figures/figures/fmriprep_figures/XCPD_task-{task}_StandardDeviation.png")
        plt.close()

        # --- Plot colorbars ---
        fig, axs = plt.subplots(2, 1, figsize=(10, 1.5))
        norm = mpl.colors.Normalize(vmin=-1, vmax=1)
        fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap="seismic"), cax=axs[0], orientation="horizontal").set_ticks([-1, 0, 1])
        norm = mpl.colors.Normalize(vmin=0, vmax=vmax1)
        fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap="Reds"), cax=axs[1], orientation="horizontal").set_ticks([0, np.mean([0, vmax1]), vmax1])
        fig.tight_layout()
        fig.savefig(f"/cbica/projects/executive_function/EF_dataset_figures/figures/fmriprep_figures/XCPD_task-{task}_colorbar.png", bbox_inches="tight")
        plt.close()

