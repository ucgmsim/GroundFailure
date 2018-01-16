#!/bin/bash

run_dir=$1 #/home/nesi00213/RunFolder/Cybershake/v17p8/Runs - This allows us to change between simulation datasets (eg to v17p9)
list_runs=`cat $2`

cd /home/fordw/Scripts/CCDF_scripts_and_plots/

for run_name in $list_runs
do

  for realisation_path in `find  $run_dir/$run_name/Impact/Liquefaction/ -type d -name ""$run_name"_HYP*"` #Pull out the filepath to the directory for specific realisation of the chosen fault
  do
    realisation=$(basename $realisation_path)
    python CCDF_regional.py $realisation_path/*zhu_2016_general_probability_n*.xyz
    python CCDF_regional.py $run_dir/$run_name/Impact/Landslide/$realisation/*probability.xyz
  done
done
