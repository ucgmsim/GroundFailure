#!/bin/bash

# This script is a shorter version of /home/nesi00213/groundfailure/scripts/CCDF_Automatic.sh that ONLY runs the CCDF_regional.py 
# It was created to accommodate a small edit that allowed troubleshooting of the aforementioned python script

# This was written by Luke Longworth on 16/01/2018

run_dir=$1 # eg /home/nesi00213/RunFolder/Cybershake/v17p8/Runs - This allows us to change between simulation datasets (eg to v17p9)
list_runs=`cat $2`# A list of all relevant run names (fault names, not realisations)

cd /home/fordw/Scripts/CCDF_scripts_and_plots/ # This folder held (at the time) the most up to date version of Ford's code

for run_name in $list_runs
do
  for realisation_path in `find  $run_dir/$run_name/Impact/Liquefaction/ -type d -name ""$run_name"_HYP*"` #Pull out the filepath to the directory for specific realisation of the chosen fault
  do
    realisation=$(basename $realisation_path) # Take just the realisation name, not the full filepath
    python CCDF_regional.py $realisation_path/*zhu_2016_general_probability_n*.xyz # Run the script on the particular liq.xyz file
    python CCDF_regional.py $run_dir/$run_name/Impact/Landslide/$realisation/*probability.xyz # Run the script on the landslide .xyz file
  done
done
