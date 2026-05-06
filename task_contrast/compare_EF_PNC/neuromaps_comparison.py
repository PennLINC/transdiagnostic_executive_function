######Create statistical null
from neuromaps import datasets, images, nulls, resampling, transforms
EF = "/cbica/projects/executive_function/code/task_contrast/final/results/second-level/nback-rtdur/group-twoBackMinusZeroBack/group/contrast-twobackminuszeroback_stat-z_statmap.nii.gz"
PNC = "/cbica/projects/executive_function/code/task_contrast/final/task_contrast_PNC/group_zmap_MNI.nii.gz"
EF, PNC = resampling.resample_images(src=EF,trg=PNC, resampling = 'transform_to_alt', alt_spec=('fsLR','32k'), src_space='MNI152', trg_space='MNI152')

from netneurotools import datasets as nntdata
from neuromaps.parcellate import Parcellater
from neuromaps.images import dlabel_to_gifti

schaefer = nntdata.fetch_schaefer2018('fslr32k')['400Parcels7Networks']
parcimg = dlabel_to_gifti(schaefer)
parc = Parcellater(parcimg, 'fsLR')
EF_parcellated_data = parc.fit_transform(EF, 'fsLR')
PNC_parcellated_data = parc.fit_transform(PNC, 'fsLR')

rotated = nulls.alexander_bloch(EF_parcellated_data, atlas='fsLR', density='32k',
                                n_perm=10000, seed=1234, parcellation=parcimg)
print(rotated.shape)

######Compare images
from neuromaps import stats
corr, pval = stats.compare_images(EF_parcellated_data, PNC_parcellated_data, nulls=rotated)
print(f'r = {corr:.3f}, p = {pval:.3f}')


######Plot as scatterplot
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

x = EF_parcellated_data
y = PNC_parcellated_data

mask = np.isfinite(x) & np.isfinite(y)
x = x[mask]
y = y[mask]

plt.figure(figsize=(4, 4))
print("x/y n:", x.size, y.size)

sns.regplot(
    x=x,
    y=y,
    scatter_kws={
        "s": 12,
        "alpha": 0.6,
        "color": "royalblue",
        "edgecolor": "none",
    },
    line_kws={
        "linewidth": 2,
    },
    ci=None,
)

plt.title(f"r = {corr:.3f}, p(spin) = {pval:.4f}")
plt.xlabel("EF")
plt.ylabel("PNC")
plt.tight_layout()

out_dir = "/cbica/projects/executive_function/code/task_contrast/final/compare_EF_PNC"
os.makedirs(out_dir, exist_ok=True)

plt.savefig(
    os.path.join(out_dir, "scatterplot.pdf"),
    bbox_inches="tight",
    transparent=True,
)
plt.close()
