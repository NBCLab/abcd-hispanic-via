import os
import os.path as op
import pandas as pd
import subprocess
from nilearn import masking
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


project_directory = '/home/data/abcd/abcd-hispanic-via/'
derivative_directory = op.join(project_directory, 'dset/derivatives/fmriprep_post-process_Cluster1+Cluster2+Cluster3+Cluster4+Cluster5+Cluster6')

analyses_directory = 'group-comparison/rest-group-Cluster1'

#start with the covariates file
covar = pd.read_csv(op.join(derivative_directory, analyses_directory, 'covariates_file.txt'), sep='\s+')

#first add the summary scores
#parent prosocial behavior and family conflict subscale
sscep = pd.read_csv(op.join(project_directory, 'code', 'abcdclinicaldata05032021', 'abcd_sscep01.txt'), sep='\t')
# prosocial variable: psb_p_ss_mean
# fes variable: fes_p_ss_fc
psb_p = []
fes_p = []
for i, row in covar.iterrows():
    tmp_df = sscep[(sscep['subjectkey']=='NDAR_{}'.format(row['subject'].split('sub-NDAR')[1])) & (sscep['eventname']=='baseline_year_1_arm_1')]

    psb_p.append(tmp_df['psb_p_ss_mean'].values[0])
    fes_p.append(tmp_df['fes_p_ss_fc'].values[0])

#now youth
sscey = pd.read_csv(op.join(project_directory, 'code', 'abcdclinicaldata05032021', 'abcd_sscey01.txt'), sep='\t')
# prosocial variable: psb_p_ss_mean
psb_y = []
for i, row in covar.iterrows():
    tmp_df = sscey[(sscey['subjectkey']=='NDAR_{}'.format(row['subject'].split('sub-NDAR')[1])) & (sscey['eventname']=='baseline_year_1_arm_1')]

    psb_y.append(tmp_df['psb_y_ss_mean'].values[0])

#cbcl stuff
cbcl = pd.read_csv(op.join(project_directory, 'code', 'abcdclinicaldata05032021', 'abcd_cbcls01.txt'), sep='\t')
# cbcl variables
cbcl_scr_syn_anxdep_t = []
cbcl_scr_syn_withdep_t = []
cbcl_scr_syn_internal_t = []
cbcl_scr_syn_external_t = []
cbcl_scr_dsm5_depress_t = []
cbcl_scr_syn_rulebreak_t = []
cbcl_scr_syn_attention_t = []
cbcl_scr_syn_aggressive_t =[]
cbcl_scr_dsm5_opposit_t = []
cbcl_scr_dsm5_adhd_t = []
cbcl_scr_dsm5_opposit_r = []

for i, row in covar.iterrows():
    tmp_df = cbcl[(cbcl['subjectkey']=='NDAR_{}'.format(row['subject'].split('sub-NDAR')[1])) & (cbcl['eventname']=='baseline_year_1_arm_1')]
    cbcl_scr_syn_anxdep_t.append(tmp_df['cbcl_scr_syn_anxdep_t'].values[0])
    cbcl_scr_syn_withdep_t.append(tmp_df['cbcl_scr_syn_withdep_t'].values[0])
    cbcl_scr_syn_internal_t.append(tmp_df['cbcl_scr_syn_internal_t'].values[0])
    cbcl_scr_syn_external_t.append(tmp_df['cbcl_scr_syn_external_t'].values[0])
    cbcl_scr_dsm5_depress_t.append(tmp_df['cbcl_scr_dsm5_depress_t'].values[0])
    cbcl_scr_syn_rulebreak_t.append(tmp_df['cbcl_scr_syn_rulebreak_t'].values[0])
    cbcl_scr_syn_attention_t.append(tmp_df['cbcl_scr_syn_attention_t'].values[0])
    cbcl_scr_syn_aggressive_t.append(tmp_df['cbcl_scr_syn_aggressive_t'].values[0])
    cbcl_scr_dsm5_opposit_t.append(tmp_df['cbcl_scr_dsm5_opposit_t'].values[0])
    cbcl_scr_dsm5_adhd_t.append(tmp_df['cbcl_scr_dsm5_adhd_t'].values[0])
    cbcl_scr_dsm5_opposit_r.append(tmp_df['cbcl_scr_dsm5_opposit_r'].values[0])

#get ROI values
#roi_mask_fn = op.join(derivative_directory, analyses_directory, 'both_GroupCProb1-GroupCProb2_Zscr.p001.p05.minextent=154_mask.nii.gz')
#roi_fn = op.join(derivative_directory, analyses_directory, 'both_GroupCProb1-GroupCProb2_Zscr.p001.p05.minextent=154.nii.gz')
roi_mask_fn = op.join(derivative_directory, analyses_directory, 'GroupCProb1-GroupCProb2_Zscr_cluster-1_mask.nii.gz')

roi_values = []
for i, row in covar.iterrows():
    tmp_img_fn = op.join(derivative_directory, row['subject'], 'ses-baselineYear1Arm1', 'rest-Cluster1+tlrc.BRIK')
    roi_values.append(np.mean(masking.apply_mask(tmp_img_fn, roi_mask_fn)))
    #roi_values.append(np.average(masking.apply_mask(tmp_img_fn, roi_mask_fn), weights=[masking.apply_mask(roi_fn, roi_mask_fn)]))

#get group assignment
detached = []
bicultural = []
group = []
lpa_df = pd.read_csv(op.join(project_directory, 'code', 'LPAResults.csv'), sep=',')
for i, row in covar.iterrows():
    tmp_df = lpa_df[lpa_df['subjectkey']=='NDAR_{}'.format(row['subject'].split('sub-NDAR')[1])]
    if tmp_df['CProb1'].values[0] > 0.7:
        detached.append(1)
        bicultural.append(0)
        group.append(1)
    elif tmp_df['CProb2'].values[0] > 0.7:
        detached.append(0)
        bicultural.append(1)
        group.append(2)
    else:
        detached.append(0)
        bicultural.append(0)
        group.append(3)

covar['psb_p_ss_mean'] = psb_p
covar['fes_p_ss_fc'] = fes_p
covar['psb_y_ss_mean'] = psb_y
covar['roi_value'] = roi_values
covar['detached'] = detached
covar['bicultural'] = bicultural
covar['group'] = group
covar['cbcl_scr_syn_anxdep_t'] = cbcl_scr_syn_anxdep_t
covar['cbcl_scr_syn_withdep_t'] = cbcl_scr_syn_withdep_t
covar['cbcl_scr_syn_internal_t'] = cbcl_scr_syn_internal_t
covar['cbcl_scr_syn_external_t'] = cbcl_scr_syn_external_t
covar['cbcl_scr_dsm5_depress_t'] = cbcl_scr_dsm5_depress_t
covar['cbcl_scr_syn_rulebreak_t'] = cbcl_scr_syn_rulebreak_t
covar['cbcl_scr_syn_attention_t'] = cbcl_scr_syn_attention_t
covar['cbcl_scr_syn_aggressive_t'] = cbcl_scr_syn_aggressive_t
covar['cbcl_scr_dsm5_opposit_t'] = cbcl_scr_dsm5_opposit_t
covar['cbcl_scr_dsm5_adhd_t'] = cbcl_scr_dsm5_adhd_t
covar['cbcl_scr_dsm5_opposit_r'] = cbcl_scr_dsm5_opposit_r

#covar = covar.fillna(0)
covar.to_csv(op.join(derivative_directory, analyses_directory, 'roi_values+behavior_cluster-1.csv'), sep='\t')

exit()
sns.lmplot(x="roi_value", y="psb_p_ss_mean", hue="group", data=covar, height=10)
plt.xlabel("Correlation (r)")
plt.ylabel("Prosocial Behaviors Parent")
plt.savefig(op.join(derivative_directory, analyses_directory, 'psb_p_correlation.png'), format='png',dpi=150)
plt.close()

sns.lmplot(x="roi_value", y="fes_p_ss_fc", hue="group", data=covar, height=10)
plt.xlabel("Correlation (r)")
plt.ylabel("Family Conflict")
plt.savefig(op.join(derivative_directory, analyses_directory, 'fes_p_ss_fc_correlation.png'), format='png',dpi=150)
plt.close()

sns.lmplot(x="roi_value", y="psb_y_ss_mean", hue="group", data=covar, height=10)
plt.xlabel("Correlation (r)")
plt.ylabel("Prosocial Behaviors Youth")
plt.savefig(op.join(derivative_directory, analyses_directory, 'psb_y_correlation.png'), format='png',dpi=150)
plt.close()
