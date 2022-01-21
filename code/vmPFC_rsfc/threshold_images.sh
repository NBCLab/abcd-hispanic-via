project_directory='/home/data/abcd/abcd-hispanic-via'

analyses_directory=$project_directory/dset/derivatives/fmriprep_post-process_Cluster1+Cluster2+Cluster3+Cluster4+Cluster5+Cluster6/group-comparison_0.7

pval=$(ptoz 0.05 -2) # 0.001
for analysis in 'rest-group-Cluster1' 'rest-group-Cluster2' 'rest-group-Cluster3' 'rest-group-Cluster4' 'rest-group-Cluster5' 'rest-group-Cluster6'; do
  cluster=${analysis##*-}
  labels=$(3dinfo -label -sb_delim " " $analyses_directory/$analysis/rest-$cluster+tlrc)
  labels="Bicult-Detached_Zscr"
  echo $labels
  label_count=0
  label_count=1
  for label in $labels; do
    echo $label
    3dAFNItoNIFTI -prefix $analyses_directory/$analysis/$label.nii.gz $analyses_directory/$analysis/rest-$cluster+tlrc.BRIK\'[$label_count]\'

    csize=`1dcat $analyses_directory/$analysis/rest-$cluster.CSimA.NN1_2sided.1D"{5}[6]"`
    echo $csize

    cluster --in=$analyses_directory/$analysis/$label.nii.gz --thresh=$pval --connectivity=6 --minextent=$csize --no_table --othresh=$analyses_directory/$analysis/$label.p05.p05.minextent=$csize.nii.gz
    fslmaths $analyses_directory/$analysis/$label.nii.gz -mul -1 $analyses_directory/$analysis/neg_$label.nii.gz
    cluster --in=$analyses_directory/$analysis/neg_$label.nii.gz --thresh=$pval --connectivity=6 --minextent=$csize --no_table --othresh=$analyses_directory/$analysis/neg_$label.p05.p05.minextent=$csize.nii.gz

    fslmaths $analyses_directory/$analysis/$label.p05.p05.minextent=$csize.nii.gz -sub $analyses_directory/$analysis/neg_$label.p05.p05.minextent=$csize.nii.gz $analyses_directory/$analysis/both_$label.p05.p05.minextent=$csize.nii.gz

    label_count=$((label_count + 1))
  done
done
