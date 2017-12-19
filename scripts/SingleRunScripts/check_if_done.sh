#!/bin/bash

run_dir=$1
list_runs=`cat $2`

for run_name in $list_runs
do
  for realisation_path in `find  $run_dir/$run_name/Impact/Liquefaction -type d -name ""$run_name"_HYP*"` #Pull out the filepath to the directory for specific realisation of the chosen fault
  do
    realisation=$(basename $realisation_path) #Pull out the name of the realisation without the rest of the filepath
    if [ -e $realisation_path/"$run_name"_liq_nz-specific-vs30_probability_general.png ]
      then
      :
    else
      echo $realisation has not been completed
    fi
  done
done

