#!/usr/bin/env python
"""
Project MNI maps to fsLR-32k, parcellate with Schaefer-400, and plot
the parcellated EF and PNC maps separately on the surface.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from neuromaps import transforms, datasets
from neuromaps.parcellate import Parcellater
from neuromaps.images import dlabel_to_gifti, load_gifti
from netneurotools import datasets as nntdata

from nilearn import plotting


# ============================================================
# INPUT MAPS
# ============================================================
maps = {
    "EF": Path(
        "/cbica/projects/executive_function/code/task_contrast/final/results/"
        "second-level/nback-rtdur/group-twoBackMinusZeroBack/group/"
        "contrast-twobackminuszeroback_stat-z_statmap.nii.gz"
    ),
    "PNC": Path(
        "/cbica/projects/executive_function/code/task_contrast/final/"
        "task_contrast_PNC/group_zmap_MNI.nii.gz"
    ),
}

titles = {
    "EF": "EF 2-back > 0-back (parcellated)",
    "PNC": "PNC 2-back > 0-back (parcellated)",
}

# ============================================================
# OUTPUT DIR
# ============================================================
out_dir = Path(
    "/cbica/projects/executive_function/code/task_contrast/final/"
    "figures/parcellated_surface_maps"
)
out_dir.mkdir(parents=True, exist_ok=True)


# ============================================================
# FETCH fsLR SURFACES + SCHAEFER-400 PARCELLATION
# ============================================================
# fsLR surfaces for plotting
fslr = datasets.fetch_fslr(density="32k")

# Schaefer-400 in fsLR-32k space
schaefer = nntdata.fetch_schaefer2018("fslr32k")["400Parcels7Networks"]

# Convert dlabel/cifti parcellation to left/right gifti label images
parcimg = dlabel_to_gifti(schaefer)

# Build parcellater in fsLR space
parc = Parcellater(parcimg, "fsLR")


# ============================================================
# HELPERS
# ============================================================
def flatten_parcellated(arr):
    """Make sure parcellated output is a 1D vector."""
    arr = np.asarray(arr).squeeze()
    if arr.ndim != 1:
        arr = arr.reshape(-1)
    return arr


def get_parcel_labels(n_parcels):
    """Try to fetch Schaefer labels; otherwise make generic names."""
    try:
        info = nntdata.fetch_schaefer2018()
        labels = info.get("400Parcels7Networks_order", None)
        if labels is not None and len(labels) == n_parcels:
            return [lab.decode() if isinstance(lab, bytes) else str(lab) for lab in labels]
    except Exception:
        pass
    return [f"Parcel_{i+1:03d}" for i in range(n_parcels)]


def parcels_to_vertices(parcel_values, parcimg):
    """
    Expand parcelwise values back to fsLR vertices using the Schaefer label map.

    Parameters
    ----------
    parcel_values : (n_parcels,) array
        One value per parcel.
    parcimg : tuple
        Left/right gifti label images from dlabel_to_gifti().

    Returns
    -------
    lh_vertex_data, rh_vertex_data : arrays
        Parcel values assigned to each surface vertex.
    """
    parcel_values = flatten_parcellated(parcel_values)

    lh_labels = np.asarray(load_gifti(parcimg[0]).agg_data()).squeeze().astype(int)
    rh_labels = np.asarray(load_gifti(parcimg[1]).agg_data()).squeeze().astype(int)

    # Schaefer labels are parcel IDs on the surface; 0 is medial wall/background
    all_ids = np.unique(np.concatenate([lh_labels, rh_labels]))
    all_ids = all_ids[all_ids != 0]
    all_ids = np.sort(all_ids)

    if len(all_ids) != len(parcel_values):
        raise ValueError(
            f"Number of parcel IDs on surface ({len(all_ids)}) does not match "
            f"number of parcel values ({len(parcel_values)})."
        )

    id_to_value = {pid: val for pid, val in zip(all_ids, parcel_values)}

    lh_data = np.full(lh_labels.shape, np.nan, dtype=float)
    rh_data = np.full(rh_labels.shape, np.nan, dtype=float)

    for pid, val in id_to_value.items():
        lh_data[lh_labels == pid] = val
        rh_data[rh_labels == pid] = val

    return lh_data, rh_data


def save_parcellated_table(parcel_values, map_name, out_file):
    """Save parcelwise values to TSV."""
    parcel_values = flatten_parcellated(parcel_values)
    labels = get_parcel_labels(len(parcel_values))

    df = pd.DataFrame({
        "parcel": labels,
        "value": parcel_values,
        "map": map_name,
    })
    df.to_csv(out_file, sep="\t", index=False)
    return df


def plot_parcellated_map(lh_data, rh_data, title, out_file, cmap="cold_hot"):
    """
    Plot parcellated values on fsLR surfaces using Schaefer parcel coloring.
    """
    fig = plt.figure(figsize=(12, 8))

    ax1 = fig.add_subplot(2, 2, 1, projection="3d")
    plotting.plot_surf_stat_map(
        surf_mesh=fslr["inflated"][0],
        stat_map=lh_data,
        hemi="left",
        view="lateral",
        bg_map=fslr["sulc"][0],
        colorbar=True,
        cmap=cmap,
        title=f"{title} (LH lateral)",
        axes=ax1,
        darkness=None,
    )

    ax2 = fig.add_subplot(2, 2, 2, projection="3d")
    plotting.plot_surf_stat_map(
        surf_mesh=fslr["inflated"][1],
        stat_map=rh_data,
        hemi="right",
        view="lateral",
        bg_map=fslr["sulc"][1],
        colorbar=False,
        cmap=cmap,
        title=f"{title} (RH lateral)",
        axes=ax2,
        darkness=None,
    )

    ax3 = fig.add_subplot(2, 2, 3, projection="3d")
    plotting.plot_surf_stat_map(
        surf_mesh=fslr["inflated"][0],
        stat_map=lh_data,
        hemi="left",
        view="medial",
        bg_map=fslr["sulc"][0],
        colorbar=False,
        cmap=cmap,
        title=f"{title} (LH medial)",
        axes=ax3,
        darkness=None,
    )

    ax4 = fig.add_subplot(2, 2, 4, projection="3d")
    plotting.plot_surf_stat_map(
        surf_mesh=fslr["inflated"][1],
        stat_map=rh_data,
        hemi="right",
        view="medial",
        bg_map=fslr["sulc"][1],
        colorbar=False,
        cmap=cmap,
        title=f"{title} (RH medial)",
        axes=ax4,
        darkness=None,
    )

    plt.savefig(
        out_file,
        bbox_inches="tight",
        dpi=300,
        facecolor="white",
        transparent=False,
    )
    plt.close(fig)


# ============================================================
# MAIN
# ============================================================
for key, path in maps.items():
    print(f"\n--- {key} ---")
    print(f"Input MNI map: {path}")

    # 1) Project MNI volumetric map to fsLR 32k
    surf_map = transforms.mni152_to_fslr(str(path), fslr_density="32k")
    print("Projected to fsLR 32k.")

    # 2) Parcellate projected surface map with Schaefer-400
    parcel_values = parc.fit_transform(surf_map, "fsLR")
    parcel_values = flatten_parcellated(parcel_values)
    print(f"Parcellated: {parcel_values.shape[0]} parcels.")

    # 3) Save parcelwise table
    tsv_file = out_dir / f"{key}_fsLR32k_Schaefer400.tsv"
    df = save_parcellated_table(parcel_values, key, tsv_file)
    print(f"Saved parcel TSV: {tsv_file}")

    # Optional ranked version
    ranked_file = out_dir / f"{key}_fsLR32k_Schaefer400_ranked.tsv"
    df.assign(abs_value=df["value"].abs()) \
      .sort_values("abs_value", ascending=False) \
      .to_csv(ranked_file, sep="\t", index=False)
    print(f"Saved ranked parcel TSV: {ranked_file}")

    # 4) Expand parcel values back to vertices for plotting
    lh_data, rh_data = parcels_to_vertices(parcel_values, parcimg)

    # 5) Plot parcellated map on fsLR surface
    fig_file = out_dir / f"{key}_fsLR32k_Schaefer400_surface.pdf"
    plot_parcellated_map(
        lh_data=lh_data,
        rh_data=rh_data,
        title=titles[key],
        out_file=fig_file,
        cmap="cold_hot",
    )
    print(f"Saved parcellated surface figure: {fig_file}")

print("\nDone.")
