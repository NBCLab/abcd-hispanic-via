import json
import os
import os.path as op
from glob import glob

import pandas as pd

"""
proj_dir = "/home/data/abcd/abcd-hispanic-via"

participants_fn = op.join(proj_dir, "code", "LPAResults.csv")

participants_df = pd.read_csv(participants_fn, sep="\t")

subids = []
for i, row in participants_df.iterrows():
    subids.append("sub-{}".format(row["subjectkey"].replace("_", "")))

participants_df["participant_id"] = subids
participants_df.to_csv(op.join(proj_dir, "dset", "participants.tsv"), sep="\t", index=False)
"""

# Add Manufacturer name
dset = "/home/data/abcd/abcd-hispanic-via/dset"
participant_fn = op.join(dset, "participants.tsv")
participant_df = pd.read_csv(participant_fn, sep="\t")
participant_ids = participant_df["participant_id"].tolist()
n_participants = len(participant_ids)
scanner_lst = []
participant_philips = participant_df[participant_df["Manufacturer"] == "Philips"][
    "participant_id"
].tolist()
participant_ge = participant_df[participant_df["Manufacturer"] == "GE"]["participant_id"].tolist()
# print(participant_philips)
# print(participant_ge)
for ppt_ph in participant_philips:
    sub = op.join(dset, ppt_ph)
    mriqcs = glob(op.join(dset, "derivatives", "mriqc-0.16.1", f"{ppt_ph}*"))
    fmripreps = glob(op.join(dset, "derivatives", "fmriprep-21.0.0", f"{ppt_ph}*"))
    # print(sub, mriqc, fmriprep)
    if op.exists(sub):
        os.system(f"rm -rf {sub}")
    for mriqc in mriqcs:
        if op.exists(mriqc):
            os.system(f"rm -rf {mriqc}")
    for fmriprep in fmripreps:
        if op.exists(fmriprep):
            os.system(f"rm -rf {fmriprep}")

for ppt_ph in participant_ge:
    sub = op.join(dset, ppt_ph)
    mriqcs = glob(op.join(dset, "derivatives", "mriqc-0.16.1", f"{ppt_ph}*"))
    fmripreps = glob(op.join(dset, "derivatives", "fmriprep-21.0.0", f"{ppt_ph}*"))
    # print(sub, mriqc, fmriprep)
    if op.exists(sub):
        os.system(f"rm -rf {sub}")
    for mriqc in mriqcs:
        if op.exists(mriqc):
            os.system(f"rm -rf {mriqc}")
    for fmriprep in fmripreps:
        if op.exists(fmriprep):
            os.system(f"rm -rf {fmriprep}")

"""
for participant_id in participant_ids:
    json_files = glob(op.join(dset, participant_id, "*", "*", "*.json"))

    if len(json_files) == 0:
        scanner = ""
    else:
        with open(json_files[0], "r") as fo:
            json_info = json.load(fo)
        scanner = json_info["Manufacturer"]
    scanner_lst.append(scanner)


assert len(scanner_lst) == n_participants

# participant_df.insert(4, "Manufacturer", scanner_lst)
# print(participant_df)
# participant_df.to_csv(participant_fn, sep="\t", index=False)
"""
