#!/usr/bin/env python3
"""
Based on
https://github.com/BIDS-Apps/example/blob/aa0d4808974d79c9fbe54d56d3b47bb2cf4e0a0d/run.py
"""
import os
import os.path as op
from glob import glob

import nibabel as nib
import numpy as np
import pandas as pd
from nilearn import masking

bids_dir = "/home/data/abcd/abcd-hispanic-via/dset"
mriqc_dir = op.join(bids_dir, "derivatives", "mriqc-0.15.1")
curr_dir = os.getcwd()

pid_df = pd.read_csv(op.join(bids_dir, "participants.tsv"), sep="\t")
pid = pid_df["participant_id"]

behavioral_df = pd.read_csv(
    op.join(
        op.dirname(bids_dir),
        "code",
        "ltnx_demo_via_lt_acspsw03_asr_cbcl_crpbi_pmq_pfe_pfes_tbss.csv",
    ),
    sep="\t",
)
site_dict = {site: i for i, site in enumerate(behavioral_df["site_id_l"].unique())}
lpa_df = pd.read_csv(op.join(op.dirname(bids_dir), "code", "LPAResults.csv"), sep="\t")

derivative = "fmriprep_post-process"
out_dir = op.join(bids_dir, "derivatives", derivative, "nback-group-avg")
os.makedirs(out_dir, exist_ok=True)

if not op.isfile(op.join(out_dir, "group_bold.tsv")):
    mriqc_version = "0.15.1"
    singularity_images_home = "/home/data/cis/singularity-images"
    mriqc_image = op.join(
        singularity_images_home,
        "poldracklab_mriqc_{mriqc_version}.sif".format(mriqc_version=mriqc_version),
    )

    # run mrqic to generate group level statistics
    cmd = "singularity run --cleanenv \
               {mriqc_image} {bids_dir} {mriqc_dir} \
               group --no-sub --task-id nback".format(
        mriqc_image=mriqc_image, bids_dir=bids_dir, mriqc_dir=mriqc_dir
    )
    os.system(cmd)
    os.rename(op.join(mriqc_dir, "group_bold.tsv"), op.join(out_dir, "group_bold.tsv"))
    os.rename(op.join(mriqc_dir, "group_bold.html"), op.join(out_dir, "group_bold.html"))

mriqc_group_df = pd.read_csv(op.join(out_dir, "group_bold.tsv"), sep="\t")

# get task specific runs
mriqc_group_nback_df = mriqc_group_df[mriqc_group_df["bids_name"].str.contains("nback")]

# functional qc metrics of interest
qc_metrics = ["efc", "snr", "fd_mean", "tsnr", "gsr_x", "gsr_y"]
runs_exclude_df = pd.DataFrame()
for qc_metric in qc_metrics:
    q99, q01 = np.percentile(mriqc_group_nback_df[qc_metric].values, [99, 1])
    if qc_metric in ["efc", "fd_mean", "gsr_x", "gsr_y"]:
        runs_exclude_df = runs_exclude_df.append(
            mriqc_group_nback_df.loc[mriqc_group_nback_df[qc_metric].values > q99],
            ignore_index=True,
        )
    elif qc_metric in ["snr", "tsnr"]:
        runs_exclude_df = runs_exclude_df.append(
            mriqc_group_nback_df.loc[mriqc_group_nback_df[qc_metric].values < q01],
            ignore_index=True,
        )

# drop duplicates
runs_exclude_count = runs_exclude_df["bids_name"].value_counts()
runs_exclude_df = runs_exclude_df[
    runs_exclude_df["bids_name"].isin(runs_exclude_count[runs_exclude_count > 1].index)
]
runs_exclude_df = runs_exclude_df.drop_duplicates()
runs_exclude_df.to_csv(op.join(out_dir, "runs_to_exclude.tsv"), sep="\t", index=False)

# make a mask
nback_masks = sorted(
    glob(
        op.join(
            bids_dir,
            "derivatives",
            derivative,
            "sub-*",
            "ses-*",
            "nback",
            "*nback*desc-mask.nii.gz",
        )
    )
)
nback_briks = sorted(
    glob(
        op.join(bids_dir, "derivatives", derivative, "sub-*", "ses-*", "nback", "*nback*tlrc*HEAD")
    )
)

nback_masks = [i for i in nback_masks if "run-1+2" not in i]
nback_briks = [i for i in nback_briks if "run-1+2" not in i]

for i, row in runs_exclude_df.iterrows():
    tmp_run = row["bids_name"].replace("run-0", "run-").strip("_bold")
    sub = tmp_run.split("_")[0]
    ses = tmp_run.split("_")[1]
    tmp_run_mask_fn = op.join(
        bids_dir,
        "derivatives",
        derivative,
        sub,
        ses,
        "nback",
        "{}_space-MNI152NLin2009cAsym_res-2_desc-mask.nii.gz".format(tmp_run),
    )
    if tmp_run_mask_fn in nback_masks:
        nback_masks.remove(tmp_run_mask_fn)

    tmp_run_brik_fn = op.join(
        bids_dir,
        "derivatives",
        derivative,
        sub,
        ses,
        "nback",
        "{}_space-MNI152NLin2009cAsym_desc-REMLbucket+SPMG+tlrc.HEAD".format(tmp_run),
    )
    if tmp_run_brik_fn in nback_briks:
        nback_briks.remove(tmp_run_brik_fn)

final_mask_list = []
for tmp_run_mask_fn in nback_masks:
    tmp_mask_fn_list = [i for i in nback_masks if tmp_run_mask_fn.split("_run-")[0] in i]
    sub = op.basename(tmp_run_mask_fn).split("_")[0]
    ses = op.basename(tmp_run_mask_fn).split("_")[1]
    if len(tmp_mask_fn_list) > 1:
        final_mask_list.append(
            op.join(
                bids_dir,
                "derivatives",
                derivative,
                sub,
                ses,
                "nback",
                "{sub}_{ses}_task-nback_run-1+2_space-MNI152NLin2009cAsym_desc-mask.nii.gz".format(
                    sub=sub, ses=ses
                ),
            )
        )
    elif len(tmp_mask_fn_list) == 1:
        final_mask_list.append(tmp_run_mask_fn)
final_mask_list = list(set(final_mask_list))

final_brik_list = []
for tmp_run_brik_fn in nback_briks:
    tmp_brik_fn_list = [i for i in nback_briks if tmp_run_brik_fn.split("_run-")[0] in i]
    sub = op.basename(tmp_run_brik_fn).split("_")[0]
    ses = op.basename(tmp_run_brik_fn).split("_")[1]
    if len(tmp_brik_fn_list) > 1:
        final_brik_list.append(
            op.join(
                bids_dir,
                "derivatives",
                derivative,
                sub,
                ses,
                "nback",
                "{sub}_{ses}_task-nback_run-1+2_space-MNI152NLin2009cAsym_desc-REMLbucket+SPMG+tlrc.HEAD".format(
                    sub=sub, ses=ses
                ),
            )
        )
    elif len(tmp_brik_fn_list) == 1:
        final_brik_list.append(tmp_run_brik_fn)
    fd = [
        pd.read_csv(
            op.join(
                bids_dir,
                "derivatives",
                "fmriprep-20.2.1",
                "fmriprep",
                sub,
                "ses-baselineYear1Arm1",
                "func",
                "{}_desc-confounds_timeseries.tsv".format(i.split("/")[-1].split("_space-")[0]),
            ),
            sep="\t",
        )["framewise_displacement"].mean()
        for i in tmp_brik_fn_list
    ]
    with open(op.join(op.dirname(tmp_run_brik_fn), "fd_mean.txt"), "w") as fo:
        fo.write("{}".format(np.mean(fd)))

final_brik_list = list(set(final_brik_list))
final_brik_list = [i for i in final_brik_list if op.isfile(i)]
with open(op.join(out_dir, "nback-group-briks.txt"), "w") as fo:
    for tmp_brik_fn in final_brik_list:
        fo.write("{}\n".format(tmp_brik_fn))

grp_mask = masking.intersect_masks(final_mask_list, threshold=0.5)
mask_fn = op.join(out_dir, "nback-group-mask.nii.gz")
nib.save(grp_mask, mask_fn)

label_bucket_dict = {
    "two_back_gt_zero_back": 47,
    "negative_faces_gt_neutral_faces": 53,
    "positive_faces_gt_neutral_faces": 56,
}  #'zero_back':41, 'two_back':44, 'faces_gt_places': 50,
for label in label_bucket_dict.keys():

    bucket_list = [
        "{0}[{1}]".format(i.split(".HEAD")[0], label_bucket_dict[label]) for i in final_brik_list
    ]

    ###difference line
    os.makedirs(op.join(out_dir, "nback-group-{label}".format(label=label)), exist_ok=True)
    os.chdir(op.join(out_dir, "nback-group-{label}".format(label=label)))
    cluster_bucket_fn = "nback-{}".format(label)

    with open(
        op.join(out_dir, "nback-group-{label}".format(label=label), "args_file.txt"), "w"
    ) as fo:
        fo.write("-setA Group\n")
        for brik in bucket_list:
            tmp_sub = op.basename(brik).split("_")[0]
            fo.write("{sub_id} {brik_id}\n".format(sub_id=tmp_sub, brik_id=brik))

    with open(
        op.join(out_dir, "nback-group-{label}".format(label=label), "covariates_file.txt"), "w"
    ) as fo:
        fo.write(
            "subject age_p age_c site FD education income nativity_p nativity_c gender_p gender_c\n"
        )
        for brik in bucket_list:
            tmp_sub = op.basename(brik).split("_")[0]
            with open(op.join(op.dirname(brik), "fd_mean.txt"), "r") as f:
                tmp_fd = f.read()
            sub_df = behavioral_df[
                behavioral_df["subjectkey"] == "NDAR_{}".format(tmp_sub.split("sub-NDAR")[1])
            ]
            sub_df = sub_df.fillna(0)
            fo.write(
                "{sub_id} {age_p} {age_c} {site} {FD} {education} {income} {nativity_p} {nativity_c} {gender_p} {gender_c}\n".format(
                    sub_id=tmp_sub,
                    age_p=sub_df["demo_prnt_age_v2"].values[0],
                    age_c=sub_df["interview_age"].values[0],
                    site=site_dict[sub_df["site_id_l"].values[0]],
                    FD=tmp_fd,
                    education=sub_df["demo_prnt_ed_v2"].values[0],
                    income=sub_df["demo_comb_income_v2"].values[0],
                    nativity_p=sub_df["demo_prnt_origin_v2"].values[0],
                    nativity_c=sub_df["demo_origin_v2"].values[0],
                    gender_p=sub_df["demo_prnt_gender_id_v2"].values[0],
                    gender_c=sub_df["demo_gender_id_v2"].values[0],
                )
            )

    cmd = "3dttest++ -prefix {bucket_fn} -mask {mask_fn} -Covariates {covariates_file} -Clustsim -@ < {args_file}".format(
        bucket_fn=cluster_bucket_fn,
        mask_fn=mask_fn,
        covariates_file=op.join(
            out_dir, "nback-group-{label}".format(label=label), "covariates_file.txt"
        ),
        args_file=op.join(out_dir, "nback-group-{label}".format(label=label), "args_file.txt"),
    )
    # os.system(cmd)

    # now unpaired ttest
    os.makedirs(
        op.join(
            bids_dir,
            "derivatives",
            derivative,
            "nback-group-comparison",
            "nback-group-{label}".format(label=label),
        ),
        exist_ok=True,
    )
    os.chdir(
        op.join(
            bids_dir,
            "derivatives",
            derivative,
            "nback-group-comparison",
            "nback-group-{label}".format(label=label),
        )
    )
    cluster_bucket_fn = "nback-{}".format(label)

    setA = []
    setB = []

    for brik in bucket_list:
        tmp_sub = op.basename(brik).split("_")[0]
        sub_df = lpa_df[lpa_df["subjectkey"] == "NDAR_{}".format(tmp_sub.split("sub-NDAR")[1])]
        if sub_df["CProb1"].values[0] >= 0.7:
            setA.append("{sub_id} {brik_id}\n".format(sub_id=tmp_sub, brik_id=brik))
        elif sub_df["CProb2"].values[0] >= 0.7:
            setB.append("{sub_id} {brik_id}\n".format(sub_id=tmp_sub, brik_id=brik))
        else:
            print(sub_df)

    with open(
        op.join(
            bids_dir,
            "derivatives",
            derivative,
            "nback-group-comparison",
            "nback-group-{label}".format(label=label),
            "args_file.txt",
        ),
        "w",
    ) as fo:
        fo.write(
            "-setA Bicult {setA}\n -setB Detached {setB}\n".format(
                setA=" ".join(setA), setB=" ".join(setB)
            )
        )

    with open(
        op.join(
            bids_dir,
            "derivatives",
            derivative,
            "nback-group-comparison",
            "nback-group-{label}".format(label=label),
            "covariates_file.txt",
        ),
        "w",
    ) as fo:
        fo.write(
            "subject age_p age_c site FD education income nativity_p nativity_c gender_p gender_c\n"
        )
        for brik in bucket_list:
            tmp_sub = op.basename(brik).split("_")[0]
            with open(op.join(op.dirname(brik), "fd_mean.txt"), "r") as f:
                tmp_fd = f.read()
            sub_df = behavioral_df[
                behavioral_df["subjectkey"] == "NDAR_{}".format(tmp_sub.split("sub-NDAR")[1])
            ]
            sub_df = sub_df.fillna(0)
            fo.write(
                "{sub_id} {age_p} {age_c} {site} {FD} {education} {income} {nativity_p} {nativity_c} {gender_p} {gender_c}\n".format(
                    sub_id=tmp_sub,
                    age_p=sub_df["demo_prnt_age_v2"].values[0],
                    age_c=sub_df["interview_age"].values[0],
                    site=site_dict[sub_df["site_id_l"].values[0]],
                    FD=tmp_fd,
                    education=sub_df["demo_prnt_ed_v2"].values[0],
                    income=sub_df["demo_comb_income_v2"].values[0],
                    nativity_p=sub_df["demo_prnt_origin_v2"].values[0],
                    nativity_c=sub_df["demo_origin_v2"].values[0],
                    gender_p=sub_df["demo_prnt_gender_id_v2"].values[0],
                    gender_c=sub_df["demo_gender_id_v2"].values[0],
                )
            )

    cmd = "3dttest++ -prefix {bucket_fn} -mask {mask_fn} -Covariates {covariates_file} -Clustsim -@ < {args_file}".format(
        bucket_fn=cluster_bucket_fn,
        mask_fn=mask_fn,
        covariates_file=op.join(
            bids_dir,
            "derivatives",
            derivative,
            "nback-group-comparison",
            "nback-group-{label}".format(label=label),
            "covariates_file.txt",
        ),
        args_file=op.join(
            bids_dir,
            "derivatives",
            derivative,
            "nback-group-comparison",
            "nback-group-{label}".format(label=label),
            "args_file.txt",
        ),
    )
    os.system(cmd)
    os.chdir(curr_dir)
