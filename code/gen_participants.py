import pandas as pd
import os
import os.path as op
import numpy as np


# establish project directory
proj_dir = '/Users/miriedel/Desktop/GitHub/abcd-hispanic-via'

# establish file names for the demographic and vancouver spreadsheet
demo_fn = op.join(proj_dir, 'code', 'abcdclinicaldata05032021', 'pdem02.txt')
via_fn = op.join(proj_dir, 'code', 'abcdclinicaldata05032021', 'abcd_via01.txt')

# load the vancouver spreadsheet
via_df = pd.read_csv(via_fn, sep='\t')
print('There are {} unique participant IDs '
       'and {} total responses '
       'in the Vancouver Acculturation Questionnaire.'.format(
       len(np.unique(via_df['subjectkey'])),
       len(via_df)
       ))

# identify columns specifically from the vancouver questionnaire
via_columns = [i for i in via_df.columns if 'vancouver' in i]

# find how many NAs are in each row
num_na = np.sum(pd.isna(via_df), axis=1)

# get indices where there are more NAs than half the number of vancouver
# questionnaire questions
idx_to_drop = np.where(num_na > len(via_columns)/2)[0]

# drop the rows (participants) with less than half the number of questions
# in the vancouver questionnaire completed
via_complete_df = via_df.drop(index=idx_to_drop)
print('There are {} unique participant IDs '
       'and {} total responses '
       'who completed at least half the questions '
       'in the Vancouver Acculturation Questionnaire.'.format(
       len(np.unique(via_complete_df['subjectkey'])),
       len(via_complete_df)
       ))

# load the demographic spreadsheet
demo_df = pd.read_csv(demo_fn, sep='\t')
print('There are {} unique participant IDs '
       'and {} total responses '
       'in the Demographic Questionnaire.'.format(
       len(np.unique(demo_df['subjectkey'])),
       len(demo_df)
       ))

# find the rows (participants) that are hispanic/latinx
ltnx_df = demo_df.loc[demo_df['demo_ethn_v2'].values == 1]
print('There are {} unique Latinx participant IDs '
       'and {} Latinx total responses '
       'in the Demographic Questionnaire.'.format(
       len(np.unique(ltnx_df['subjectkey'])),
       len(ltnx_df)
       ))

# create a dateframe of the vancouver questionnaire for just the hispanic/latinx IDs
via_complete_ltnx_df = via_complete_df.loc[via_complete_df['subjectkey'].isin(ltnx_df['subjectkey'])]
print('There are {} unique Latinx participant IDs '
       'and {} Latinx total responses '
        'who completed at least half the questions '
       'in the Vancouver Acculturation Questionnaire.'.format(
       len(np.unique(via_complete_ltnx_df['subjectkey'])),
       len(via_complete_ltnx_df)
       ))

via_complete_ltnx_df.to_csv(op.join(proj_dir, 'code', 'via_complete_latinx.csv'), sep='\t', index=False)
