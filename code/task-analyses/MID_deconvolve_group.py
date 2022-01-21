#!/usr/bin/env python3
"""
Based on
https://github.com/BIDS-Apps/example/blob/aa0d4808974d79c9fbe54d56d3b47bb2cf4e0a0d/run.py
"""
import os
import os.path as op
from glob import glob
from nilearn import masking
import nibabel as nib
import numpy as np
import pandas as pd

bids_dir = '/home/data/abcd/abcd-hispanic-via/dset'
mriqc_dir = op.join(bids_dir, 'derivatives', 'mriqc-0.15.1')

derivative = 'fmriprep_post-process'
out_dir = op.join(bids_dir, 'derivatives', derivative, 'MID-group-avg')
os.makedirs(out_dir, exist_ok=True)

if not op.isfile(op.join(out_dir, 'group_bold.tsv')):
    mriqc_version = '0.15.1'
    singularity_images_home = '/home/data/cis/singularity-images'
    mriqc_image = op.join(singularity_images_home, 'poldracklab_mriqc_{mriqc_version}.sif'.format(mriqc_version=mriqc_version))

    #run mrqic to generate group level statistics
    cmd = 'singularity run --cleanenv \
               {mriqc_image} {bids_dir} {mriqc_dir} \
               group --no-sub --task-id MID'.format(mriqc_image=mriqc_image,
                                                    bids_dir=bids_dir,
                                                    mriqc_dir=mriqc_dir)
    os.system(cmd)
    os.rename(op.join(mriqc_dir, 'group_bold.tsv'), op.join(out_dir, 'group_bold.tsv'))

mriqc_group_df = pd.read_csv(op.join(out_dir, 'group_bold.tsv'), sep='\t')

#get task specific runs
mriqc_group_MID_df = mriqc_group_df[mriqc_group_df['bids_name'].str.contains('MID')]

#functional qc metrics of interest
qc_metrics = ['efc', 'snr', 'fd_mean', 'tsnr', 'gsr_x', 'gsr_y']
runs_exclude_df = pd.DataFrame()
for qc_metric in qc_metrics:
    q95, q05 = np.percentile(mriqc_group_MID_df[qc_metric].values, [95, 5])
    if qc_metric in ['efc', 'fd_mean', 'gsr_x', 'gsr_y']:
        runs_exclude_df = runs_exclude_df.append(mriqc_group_MID_df.loc[mriqc_group_MID_df[qc_metric].values > q95], ignore_index=True)
    elif qc_metric in ['snr', 'tsnr']:
        runs_exclude_df = runs_exclude_df.append(mriqc_group_MID_df.loc[mriqc_group_MID_df[qc_metric].values < q05], ignore_index=True)

#drop duplicates
runs_exclude_df = runs_exclude_df.drop_duplicates()
runs_exclude_df.to_csv(op.join(out_dir, 'runs_to_exclude.tsv'), sep='\t', index=False)

#make a mask
MID_masks = sorted(glob(op.join(bids_dir, 'derivatives', derivative, 'sub-*', 'ses-*', 'MID', '*MID*desc-mask.nii.gz')))
MID_briks = sorted(glob(op.join(bids_dir, 'derivatives', derivative, 'sub-*', 'ses-*', 'MID', '*MID*tlrc*HEAD')))

MID_masks = [i for i in MID_masks if 'run-1+2' not in i]
MID_briks = [i for i in MID_briks if 'run-1+2' not in i]

for i, row in runs_exclude_df.iterrows():
    tmp_run = row['bids_name'].replace('run-0', 'run-').strip('_bold')
    sub = tmp_run.split('_')[0]
    ses = tmp_run.split('_')[1]
    tmp_run_mask_fn = op.join(bids_dir, 'derivatives', derivative, sub, ses, 'MID', '{}_space-MNI152NLin2009cAsym_res-2_desc-mask.nii.gz'.format(tmp_run))
    if tmp_run_mask_fn in MID_masks:
        MID_masks.remove(tmp_run_mask_fn)

    tmp_run_brik_fn = op.join(bids_dir, 'derivatives', derivative, sub, ses, 'MID', '{}_space-MNI152NLin2009cAsym_res-2_desc-REMLbucket+SPMG+tlrc.HEAD'.format(tmp_run))
    if tmp_run_brik_fn in MID_briks:
        MID_briks.remove(tmp_run_brik_fn)

final_mask_list = []
for tmp_run_mask_fn in MID_masks:
    tmp_mask_fn_list = [i for i in MID_masks if tmp_run_mask_fn.split('_run-')[0] in i]
    sub = op.basename(tmp_run_mask_fn).split('_')[0]
    ses = op.basename(tmp_run_mask_fn).split('_')[1]
    if len(tmp_mask_fn_list) > 1:
        final_mask_list.append(op.join(bids_dir, 'derivatives', derivative, sub, ses, 'MID', '{sub}_{ses}_task-MID_run-1+2_space-MNI152NLin2009cAsym_res-2_desc-mask.nii.gz'.format(sub=sub, ses=ses)))
    elif len(tmp_mask_fn_list) == 1:
        final_mask_list.append(tmp_run_mask_fn)
final_mask_list = list(set(final_mask_list))

final_brik_list = []
for tmp_run_brik_fn in MID_briks:
    tmp_brik_fn_list = [i for i in MID_briks if tmp_run_brik_fn.split('_run-')[0] in i]
    sub = op.basename(tmp_run_brik_fn).split('_')[0]
    ses = op.basename(tmp_run_brik_fn).split('_')[1]
    if len(tmp_brik_fn_list) > 1:
        final_brik_list.append(op.join(bids_dir, 'derivatives', derivative, sub, ses, 'MID', '{sub}_{ses}_task-MID_run-1+2_space-MNI152NLin2009cAsym_res-2_desc-REMLbucket+SPMG+tlrc.HEAD'.format(sub=sub, ses=ses)))
    elif len(tmp_brik_fn_list) == 1:
        final_brik_list.append(tmp_run_brik_fn)
final_brik_list = list(set(final_brik_list))
final_brik_list = [i for i in final_brik_list if op.isfile(i)]
with open(op.join(out_dir, 'MID-group-briks.txt'), 'w') as fo:
    for tmp_brik_fn in final_brik_list:
        fo.write('{}\n'.format(tmp_brik_fn))

grp_mask = masking.intersect_masks(final_mask_list, threshold=0.5)
mask_fn = op.join(out_dir, 'MID-group-mask.nii.gz')
nib.save(grp_mask, mask_fn)

label_bucket_dict = {'large_reward_gt_neutral_antic': 76, 'small_reward_gt_neutral_antic': 79, 'large_loss_gt_neutral_antic': 82, 'small_loss_gt_neutral_antic': 85,'reward_pos_feedback_gt_reward_neg_feedback': 88, 'loss_pos_feedback_gt_loss_neg_feedback': 91}
for label in label_bucket_dict.keys():

    bucket_fn = op.join(out_dir, 'MID-group-{label}'.format(label=label))
    bucket_list = ['{0}\'[{1}]\''.format(i.split('.HEAD')[0], label_bucket_dict[label]) for i in final_brik_list]

    cmd = '3dttest++ -prefix {bucket_fn} -mask {mask_fn} -setA {bucket_list}'.format(bucket_fn=bucket_fn, mask_fn=mask_fn, bucket_list=" ".join(bucket_list))
    os.system(cmd)
