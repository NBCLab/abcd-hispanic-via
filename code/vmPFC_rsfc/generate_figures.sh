#!/bin/bash
#SBATCH --job-name=vmPFC
#SBATCH --time=03:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem-per-cpu=2gb
#SBATCH --account=iacc_nbc
#SBATCH --qos=pq_nbc
#SBATCH --partition=IB_16C_96G
# Outputs ----------------------------------
#SBATCH --output=/home/data/abcd/abcd-hispanic-via/code/log/%x/%x-fig_%j.out
#SBATCH --error=/home/data/abcd/abcd-hispanic-via/code/log/%x/%x-fig_%j.err
# ------------------------------------------

pwd; hostname; date
set -e

source /home/data/abcd/code/abcd_fmriprep-analysis/env/environment

python /home/data/abcd/abcd-hispanic-via/code/vmPFC_rsfc/generate_figures.py

date