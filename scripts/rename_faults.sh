#!/bin/bash

# This script was written to rename the realisation so that it can be more digestible for the layman

# Usage and examples
#    bash /path/to/script/rename_faults.sh /path/to/fault/list {v17p8/v17p9} /path/to/output/directory/
#    bash /home/nesi00213/groundfailure/scripts/rename_faults.sh /home/nesi00213/RunFolder/Cybershake/v17p9/temp/list_runs_v17p9 v17p9 /home/lukelongworth/FaultNames
#    bash /home/nesi00213/groundfailure/scripts/rename_faults.sh /home/nesi00213/RunFolder/Cybershake/v17p8/temp/list_runs_v17p8

# Written by Luke Longworth for use on the USER website on 19/01/2018

# Inputs
list_runs=`cat $1` # A list of the runs you want to consider
runs=${2:-v17p8} # v17p8 or v17p9, default is v17p8
out_dir=${3:-`pwd`} # Leave blank for cwd or input a path to the output

# Useful for the loop
run_dir='/home/nesi00213/RunFolder/Cybershake/'$runs'/Runs'

# Step through the faults one by one
for run_name in $list_runs
do
  # Step through the realisations one by one.
  for realisation_path in `find  $run_dir/$run_name/GM/Validation/ -type d -name "*HYP*"`
  do
    realisation=$(basename $realisation_path) # Pull out just the realisation name itself as a variable
    python /home/nesi00213/groundfailure/scripts/rename.py $realisation $runs $out_dir # Run the rename script on the realisation
  done
done
