import os
import os.path as op
from glob import glob

import nibabel as nib
import numpy as np
from nilearn import image, masking, plotting

seed_region = "vmPFC"
hemis = "R"
FD_THR = 0.2
results_dir = f"/home/data/abcd/abcd-hispanic-via/dset/derivatives/rsfcFD{FD_THR}-{seed_region}_C1-C2-C3-C4-C5-C6/group-nonFam"
# analyses = [f"Cdinsula{hemis}", f"Cpinsula{hemis}", f"Cvinsula{hemis}"]
# analyses = ["CvmPFC1", "CvmPFC2", "CvmPFC3", "CvmPFC4", "CvmPFC5", "CvmPFC6"]
analyses = ["CvmPFC1"]
# tests = ["1SampletTest", "2SampletTest"]
tests = ["2SampletTest"]
labels = [1]
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
        for label in labels:
            img_fns = glob(
                op.join(
                    results_dir,
                    analysis,
                    f"sub-group_ses-baselineYear1Arm1_task-rest_desc-{test}{analysis}BothP*minextent*_resultL{label}.nii.gz",
                )
            )
            assert len(img_fns) == 1
            img_fn = img_fns[0]
            print(img_fn, flush=True)
            output_file = op.join(results_dir, analysis, f"{analysis}_{test}_{label}.png")

            img = nib.load(img_fn)
            min = np.min(np.abs(img.get_fdata()[np.nonzero(img.get_fdata())]))
            print(min, flush=True)

            bg_img_obj = image.load_img(bg_img)
            affine, shape = bg_img_obj.affine, bg_img_obj.shape
            # print(affine, shape, flush=True)
            img_obj = image.load_img(img)
            img_res_obj = image.resample_img(img_obj, affine, shape[:3])
            # cmap=color_dict[analysis],
            plotting.plot_stat_map(
                img_res_obj,
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
