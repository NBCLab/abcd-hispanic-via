import os
import os.path as op
from glob import glob

import nibabel as nib
import numpy as np
from nilearn import masking, plotting

results_dir = "/home/data/abcd/abcd-hispanic-via/dset/derivatives/rsfc_c1-c2-c3-c4-c5-c6/group"
analyses = ["ROI1", "ROI2", "ROI3", "ROI4", "ROI5", "ROI6"]
tests = ["1SampletTest", "2SampletTest"]
bg_img = "/home/data/cis/templateflow/tpl-MNI152NLin2009cAsym/tpl-MNI152NLin2009cAsym_res-01_desc-brain_T1w.nii.gz"

# group average
# yellow = Wistia, magenta = RdPu, cyan = bone
color_dict = {
    "ROI1": "Blues",
    "ROI2": "Wistia",
    "ROI3": "RdPu",
    "ROI4": "bone",
    "ROI5": "Reds",
    "ROI6": "Greens",
}
for test in tests:
    for analysis in analyses:
        img_fns = glob(
            op.join(
                results_dir,
                analysis,
                f"sub-group_ses-baselineYear1Arm1_task-rest_desc-{test}{analysis}BothP05minextent*_result.nii.gz",
            )
        )
        assert len(img_fns) == 1
        img_fn = img_fns[0]
        print(img_fn, flush=True)
        output_file = op.join(results_dir, analysis, f"{analysis}_{test}.png")

        img = nib.load(img_fn)
        min = np.min(np.abs(img.get_fdata()[np.nonzero(img.get_fdata())]))
        print(min, flush=True)
        # cmap=color_dict[analysis],
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
            symmetric_cbar="auto",
            dim=-0.35,
            vmax=None,
            resampling_interpolation="continuous",
        )
