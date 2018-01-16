#!/bin/bash

# Complain to Ford if you have problems

list_runs=`cat $1`
runs=${2:-v17p8}
out_dir=${3:-`pwd`}

for run_name in $list_runs
do
list_realisations=`cat /home/lukelongworth/website_data/$runs/$run_name/realisation_list.txt` # VERY, VERY, VERY BADLY HARD CODED
  for realisation in $list_realisations
  do
    python /home/nesi00213/GroundFailure/scripts/rename.py $realisation $runs $out_dir
  done
done
