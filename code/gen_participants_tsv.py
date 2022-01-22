import os
import os.path as op

import pandas as pd

proj_dir = "/home/data/abcd/abcd-hispanic-via"

participants_fn = op.join(proj_dir, "code", "LPAResults.csv")

participants_df = pd.read_csv(participants_fn, sep="\t")

subids = []
for i, row in participants_df.iterrows():
    subids.append("sub-{}".format(row["subjectkey"].replace("_", "")))

participants_df["participant_id"] = subids
participants_df.to_csv(op.join(proj_dir, "dset", "participants.tsv"), sep="\t", index=False)
