import os
import os.path as op
from glob import glob

import nibabel as nib
import numpy as np
from nilearn import masking, plotting

project_directory = "/home/data/abcd/abcd-hispanic-via"
results_dir = op.join(
    project_directory,
    "dset",
    "derivatives",
    "fmriprep_post-process_Cluster1+Cluster2+Cluster3+Cluster4+Cluster5+Cluster6",
)

analyses = [
    "rest-group-Cluster1",
    "rest-group-Cluster2",
    "rest-group-Cluster3",
    "rest-group-Cluster4",
    "rest-group-Cluster5",
    "rest-group-Cluster6",
]
bg_img = "/home/data/cis/templateflow/tpl-MNI152NLin2009cAsym/tpl-MNI152NLin2009cAsym_res-01_desc-brain_T1w.nii.gz"

# group average
# yellow = Wistia, magenta = RdPu, cyan = bone
color_dict = {
    "rest-group-Cluster1": "Blues",
    "rest-group-Cluster2": "Wistia",
    "rest-group-Cluster3": "RdPu",
    "rest-group-Cluster4": "bone",
    "rest-group-Cluster5": "Reds",
    "rest-group-Cluster6": "Greens",
}

for analysis in analyses:
    img_fn = glob(
        op.join(results_dir, "group-avg", analysis, "Group_Zscr.p0001.p05.minextent=*.nii.gz")
    )[0]
    output_file = op.join(
        results_dir, "group-avg", analysis, "{0}_{1}.png".format(analysis, op.basename(img_fn))
    )

    img = nib.load(img_fn)
    min = np.min(img.get_fdata()[np.nonzero(img.get_fdata())])

    plotting.plot_stat_map(
        img,
        bg_img=bg_img,
        cut_coords=None,
        output_file=output_file,
        display_mode="ortho",
        colorbar=True,
        threshold=min,
        annotate=False,
        draw_cross=False,
        black_bg=False,
        cmap=color_dict[analysis],
        symmetric_cbar="auto",
        dim=-0.35,
        vmax=None,
        resampling_interpolation="continuous",
    )
