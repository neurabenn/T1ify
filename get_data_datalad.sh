# NB! Install and configure access to data beforehand as described in http://datasets.datalad.org/?dir=/hcp-openaccess README under "Data access"

# random samples to download
SAMPLES=100
# download files only matching
REGEX=T1w/*_restore_brain.nii.gz

if [ ! -d "hcp_openacess" ]; then
	datalad install ///hcp-openaccess -r --recursion-limit 3
fi

#clear available subjects ids list
> available_subjects.txt

ls hcp-openaccess/HCP1200 |sort -R |tail -$SAMPLES | while read file; do
	echo "$file" >> available_subjects.txt
	datalad get hcp-openaccess/HCP1200/$file/T1w/T1w_acpc_restore_brain.nii.gz
	datalad get hcp-openaccess/HCP1200/$file/T1w/T2w_acpc_restore_brain.nii.gz	
done
