#!/bin/bash
#SBATCH --job-name=vmPFC
#SBATCH --time=50:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=30
#SBATCH --mem-per-cpu=2gb
#SBATCH --account=iacc_nbc
#SBATCH --qos=pq_nbc
#SBATCH --partition=IB_40C_512G
# Outputs ----------------------------------
#SBATCH --output=/home/data/abcd/abcd-hispanic-via/code/log/%x/%x_%A-%a.out
#SBATCH --error=/home/data/abcd/abcd-hispanic-via/code/log/%x/%x_%A-%a.err
# ------------------------------------------

pwd; hostname; date
set -e

# sbatch --array=0-5 vmPFC-group_job.sh

#==============Shell script==============#
#Load the software needed
source /home/data/abcd/code/abcd_fmriprep-analysis/env/environment
mriqc_ver=0.16.1
fmriprep_ver=21.0.0
afni_ver=20.2.10


DSET_DIR="/home/data/abcd/abcd-hispanic-via"
BIDS_DIR="${DSET_DIR}/dset"
CODE_DIR="${DSET_DIR}/code"
DERIVS_DIR="${BIDS_DIR}/derivatives"
FMRIPREP_DIR="${DERIVS_DIR}/fmriprep-${fmriprep_ver}"
MRIQC_DIR="${DERIVS_DIR}/mriqc-${mriqc_ver}"
CLEAN_DIR="${DERIVS_DIR}/denoising-${afni_ver}"
RSFC_DIR="${DERIVS_DIR}/rsfc-vmPFC_C1-C2-C3-C4-C5-C6"

session="ses-baselineYear1Arm1"
group="nonFam"

# Run group analysis
ROIs=("ROI1" "ROI2" "ROI3" "ROI4" "ROI5" "ROI6")
ROI=${ROIs[${SLURM_ARRAY_TASK_ID}]}
analysis="python ${CODE_DIR}/vmPFC_rsfc/vmPFC-group.py \
          --dset  ${BIDS_DIR} \
          --mriqc_dir ${MRIQC_DIR} \
          --preproc_dir ${FMRIPREP_DIR} \
          --clean_dir ${CLEAN_DIR} \
          --rsfc_dir  ${RSFC_DIR} \
          --session ${session} \
          --group ${group} \
          --roi ${ROI} \
          --n_rois ${#ROIs[@]} \
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