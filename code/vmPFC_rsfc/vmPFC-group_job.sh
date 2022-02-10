#!/bin/bash
#SBATCH --job-name=vmPFC
#SBATCH --time=100:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=2gb
#SBATCH --account=iacc_nbc
#SBATCH --qos=pq_nbc
#SBATCH --partition=IB_16C_96G
# Outputs ----------------------------------
#SBATCH --output=/home/data/abcd/abcd-hispanic-via/code/log/%x/%x_%j.out
#SBATCH --error=/home/data/abcd/abcd-hispanic-via/code/log/%x/%x_%j.err
# ------------------------------------------

pwd; hostname; date
set -e

# sbatch --array=1-$(( $( wc -l /home/data/abcd/abcd-hispanic-via/dset/participants.tsv | cut -f1 -d' ' ) - 1 ))%2 3dTproject_job.sbatch

#==============Shell script==============#
#Load the software needed
source /home/data/abcd/code/abcd_fmriprep-analysis/env/environment
mriqc_ver=0.16.1
fmriprep_ver=21.0.0
afni_ver=20.2.06


DSET_DIR="/home/data/abcd/abcd-hispanic-via"
BIDS_DIR="${DSET_DIR}/dset"
CODE_DIR="${DSET_DIR}/code"
DERIVS_DIR="${BIDS_DIR}/derivatives"
FMRIPREP_DIR="${DERIVS_DIR}/fmriprep-${fmriprep_ver}"
MRIQC_DIR="${DERIVS_DIR}/mriqc-${mriqc_ver}"
RSFC_DIR="${DERIVS_DIR}/rsfc_c1-c2-c3-c4-c5-c6"

session="ses-baselineYear1Arm1"

# Run group analysis
analysis="python ${CODE_DIR}/vmPFC_rsfc/vmPFC-group.py \
          --dset  ${BIDS_DIR} \
          --mriqc_dir ${MRIQC_DIR} \
          --preproc_dir ${FMRIPREP_DIR} \
          --rsfc_dir  ${RSFC_DIR} \
          --session ${session} \
          --n_rois 6 \
          --n_jobs ${SLURM_CPUS_PER_TASK}"
# Setup done, run the command
echo
echo Commandline: $analysis
eval $analysis 
exitcode=$?

# Run threshold_images.sh


echo Finished tasks with exit code $exitcode
date

exit $exitcode