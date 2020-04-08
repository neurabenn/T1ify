# NB! Install and configure access to data beforehand as described in http://datasets.datalad.org/?dir=/hcp-openaccess README under "Data access"

# random samples to download
SAMPLES=${1-10}
SUBJECTS_LIST=${1-available_subjects_hcp_t1t2.txt}

if [ ! -d "hcp_openacess" ]; then
	datalad install ///hcp-openaccess 
fi

# move to the datalad repo root
cd hcp-openaccess

#sort random on subdirectories of HCP1200 (which stand for different samples data
ls HCP1200 |sort -R |tail -$SAMPLES | while read sample; do
	# add subject to downloaded
	echo "$sample" >> ../$SUBJECTS_LIST
	datalad get HCP1200/$sample/T1w/T1w_acpc_dc_restore_brain.nii.gz
	datalad get HCP1200/$sample/T1w/T2w_acpc_dc_restore_brain.nii.gz	
done

cd ..
while read sample; do
	mkdir -p hcp-openaccess-t1t2/HCP1200/$sample/T1w
	cp -L hcp-openaccess/HCP1200/$sample/T1w/T1w_acpc_dc_restore_brain.nii.gz hcp-openaccess-t1t2/HCP1200/$sample/T1w/
	cp -L hcp-openaccess/HCP1200/$sample/T1w/T2w_acpc_dc_restore_brain.nii.gz hcp-openaccess-t1t2/HCP1200/$sample/T1w/
done < $SUBJECTS_LIST

