project_directory='/home/data/abcd/abcd-hispanic-via'

analyses_directory=$project_directory/dset/derivatives/fmriprep_post-process_resAmygdalaR_ConsensusMPM_3--1+resAmygdalaR_ConsensusMPM_3--2+resAmygdalaR_ConsensusMPM_3--3/group-comparison

pval=$(ptoz 0.001 -2)
for analysis in 'rest-group-resAmygdalaR_ConsensusMPM_3--1' 'rest-group-resAmygdalaR_ConsensusMPM_3--2' 'rest-group-resAmygdalaR_ConsensusMPM_3--3'; do
  cluster=${analysis##*rest-group-}
  labels=$(3dinfo -label -sb_delim " " $analyses_directory/$analysis/rest-$cluster+tlrc)
  labels="Bicult-Detached_Zscr"
  echo $labels
  label_count=0
  label_count=1
  for label in $labels; do
    echo $label
    3dAFNItoNIFTI -prefix $analyses_directory/$analysis/$label.nii.gz $analyses_directory/$analysis/rest-$cluster+tlrc.BRIK\'[$label_count]\'

    csize=`1dcat $analyses_directory/$analysis/rest-$cluster.CSimA.NN2_2sided.1D"{16}[6]"`

    cluster --in=$analyses_directory/$analysis/$label.nii.gz --thresh=$pval --minextent=$csize --no_table --othresh=$analyses_directory/$analysis/$label.p001.p05.minextent=$csize.nii.gz
    fslmaths $analyses_directory/$analysis/$label.nii.gz -mul -1 $analyses_directory/$analysis/neg_$label.nii.gz
    cluster --in=$analyses_directory/$analysis/neg_$label.nii.gz --thresh=$pval --minextent=$csize --no_table --othresh=$analyses_directory/$analysis/neg_$label.p001.p05.minextent=$csize.nii.gz

    fslmaths $analyses_directory/$analysis/$label.p001.p05.minextent=$csize.nii.gz -sub $analyses_directory/$analysis/neg_$label.p001.p05.minextent=$csize.nii.gz $analyses_directory/$analysis/both_$label.p001.p05.minextent=$csize.nii.gz

    label_count=$((label_count + 1))
  done
done
