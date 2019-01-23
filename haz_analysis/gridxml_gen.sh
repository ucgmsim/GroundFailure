#!/bin/bash

# Usage: ./gridxml_gen.sh $faultlist_file $output_dir
#This script requires GMT to be installed.

if [ "$#" -ne 2 ]; then
	echo "Usage: ./gridxml_gen.sh \$faultlist_file \$output_dir"
	echo "Currently this is hardcoded to search Cybershake 18p6 IMs and the 18p6 non-uniform grid"
	exit
fi

for fault in `cat $1`
	do
	im_file="/nesi/nobackup/nesi00213/RunFolder/Cybershake/v18p6_rerun/Runs/$fault/${fault}_HYP01*/IM_calc/${fault}*.csv"
	station_file="/nesi/project/nesi00213/StationInfo/non_uniform_whole_nz_with_real_stations-hh400_v18p6.ll"
	python grd2grid.py $im_file $station_file $fault $2
	mv $2/grid.xml $2/${fault}_grid.xml
done
