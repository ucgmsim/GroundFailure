#!/bin/bash

# This code steps through each realisation and creates the CCDF for liquefaction
# Inputs: 1) A filepath to the runs directory within which each fault is a subfolder
#         2) A file that contains all the fault names. This will need to be written for each set of cybershake runs (eg. v17p8)

# Usage: bash /home/lukelongworth/GroundFailure/scripts/CCDF_Automatic.sh /home/nesi00213/Runfolder/Cybershake/v17p8/Runs /home/nesi00213/Runfolder/Cybershake/v17p8/Runs/list_runs_v17p8

# Name the inputs
run_dir=$1 #/home/nesi00213/RunFolder/Cybershake/v17p8/Runs - This allows us to change between simulation datasets (eg to v17p9)
list_runs=`cat $2`

cd /home/fordw/Scripts/CCDF_scripts_and_plots

for run_name in $list_runs
do
    for realisation_path in `find  $run_dir/$run_name/Impact/Liquefaction/ -type d -name ""$run_name"_HYP*"` #Pull out the filepath to the directory for specific realisation of the chosen fault
    do
    realisation=$(basename $realisation_path) #Pull out the name of the realisation without the rest of the filepath
    #python Liq_ccdf_regional.py 
    echo $realisation_path
    done
done

