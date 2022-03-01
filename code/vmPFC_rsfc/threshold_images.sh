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
#SBATCH --output=/home/data/abcd/abcd-hispanic-via/code/log/%x/%x-img_%j.out
#SBATCH --error=/home/data/abcd/abcd-hispanic-via/code/log/%x/%x-img_%j.err
# ------------------------------------------

pwd; hostname; date
set -e

analyses_directory=/home/data/abcd/abcd-hispanic-via/dset/derivatives/rsfc-vmPFC_C1-C2-C3-C4-C5-C6/group

source /home/data/abcd/code/abcd_fmriprep-analysis/env/environment

tests=('1SampletTest' '2SampletTest')
rois=('ROI1' 'ROI2' 'ROI3' 'ROI4' 'ROI5' 'ROI6')
for test in ${tests[@]}; do
    for analysis in ${rois[@]}; do
        # labels=$(3dinfo -label -sb_delim " " ${analyses_directory}/${analysis}/sub-group_ses-baselineYear1Arm1_task-rest_desc-1SampletTest${analysis}_briks+tlrc)
        if [[ ${test} == '1SampletTest' ]]; then
            labels="Group_Zscr"
            pvoxel=0.0001
            pval=$(ptoz $pvoxel -2)
        fi

        if [[ ${test} == '2SampletTest' ]]; then
            labels="Bicult-Detached_Zscr"
            pvoxel=0.001
            pval=$(ptoz $pvoxel -2)
        fi
        
        echo $labels
        label_count=0
        label_count=1
        for label in $labels; do
            echo $label
            result_file=${analyses_directory}/${analysis}/sub-group_ses-baselineYear1Arm1_task-rest_desc-${test}${analysis}Pos_result.nii.gz
            result_neg_file=${analyses_directory}/${analysis}/sub-group_ses-baselineYear1Arm1_task-rest_desc-${test}${analysis}Neg_result.nii.gz
            brik_file=${analyses_directory}/${analysis}/sub-group_ses-baselineYear1Arm1_task-rest_desc-${test}${analysis}_briks+tlrc.BRIK
            stat_file=${analyses_directory}/${analysis}/sub-group_ses-baselineYear1Arm1_task-rest_desc-${test}${analysis}_briks.CSimA.NN1_2sided.1D

            3dAFNItoNIFTI -prefix ${result_file} ${brik_file}\'[$label_count]\'
            if [[ ${test} == '1SampletTest' ]]; then
                csize=`1dcat ${stat_file}"{22}[6]"`
            fi
            if [[ ${test} == '2SampletTest' ]]; then
                csize=`1dcat ${stat_file}"{16}[6]"`
            fi
            echo $csize

            posthr_pos_file=${analyses_directory}/${analysis}/sub-group_ses-baselineYear1Arm1_task-rest_desc-${test}${analysis}PosP${pvoxel}minextent${csize}_result.nii.gz
            posthr_neg_file=${analyses_directory}/${analysis}/sub-group_ses-baselineYear1Arm1_task-rest_desc-${test}${analysis}NegP${pvoxel}minextent${csize}_result.nii.gz
            posthr_both_file=${analyses_directory}/${analysis}/sub-group_ses-baselineYear1Arm1_task-rest_desc-${test}${analysis}BothP${pvoxel}minextent${csize}_result.nii.gz

            cluster --in=${result_file} --thresh=$pval --connectivity=6 --minextent=$csize --no_table --othresh=${posthr_pos_file}
            fslmaths ${result_file} -mul -1 ${result_neg_file}
            cluster --in=${result_neg_file} --thresh=$pval --connectivity=6 --minextent=$csize --no_table --othresh=${posthr_neg_file}

            fslmaths ${posthr_pos_file} -sub ${posthr_neg_file} ${posthr_both_file}

            label_count=$((label_count + 1))
          done
    done
done