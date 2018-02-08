#!/bin/bash


# This code runs Fill_APD_totals.py, a script written by Ford Wagner
# It steps through each realisation and runs the python script on the general_nz-specific model of liquefaction, and the landslide xyz files. 
# For more details, see the documentation of Fill_APD_totals.py

# This code is strongly modelled off CCDF_Automatic.sh

# Inputs: 1) A filepath to the runs directory within which each fault is a subfolder (must be full filepath, not using shortcuts like . or ..
#         2) A file that contains all the fault names. This will need to be written for each set of cybershake runs (eg. v17p8)
#            These can be found at /home/nesi00213/RunFolder/Cybershake/v17p8/temp/list_runs_v17p8 or equivalent for v17p9
#            The filepath should be provided such that `cat $2` outputs a list of strings

# Usage: bash /home/nesi00213/groundfailure/scripts/Run_APD.sh /home/nesi00213/Runfolder/Cybershake/v17p8/Runs /home/nesi00213/Runfolder/Cybershake/v17p8/temp/list_runs_v17p8

# This code was written on 08/02/2018 by Luke Longworth
# Contact at luke.longworth.nz@gmail.com

run_dir=$1
list_runs=`cat $2`

for run in $list_runs
do
    for realisation_path in `find $run_dir/$run/GM/Validation/ -type d -name "*HYP*"`
    do
        realisation=$(basename $realisation_path)
        python /home/fordw/Scripts/CCDF_scripts_and_plots/Fill_APD_totals.py $run_dir/$run/Impact/Liquefaction/$realisation/*general_probability_nz-specific-vs30.xyz
        python /home/fordw/Scripts/CCDF_scripts_and_plots/Fill_APD_totals.py $run_dir/$run/Impact/Landslide/$realisation/*probability.xyz
    done
done

