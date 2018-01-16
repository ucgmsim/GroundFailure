#!/bin/bash

list_runs=`cat /home/nesi00213/RunFolder/Cybershake/v17p8/temp/list_runs_v17p8`

for run_name in $list_runs #Picks a fault from the list you input (e.g. AlpineF2K)
do
  for realisation_path in `find  /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/$run_name/GM/Validation/ -type d -name ""$run_name"_HYP*"` #Pull out the filepath to the directory for specific realisation of the chosen fault
  do
    realisation=$(basename $realisation_path)
    mv /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/$run_name/Impact/Landslide/$realisation/Regional_CCDF* /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/$run_name/Impact/Landslide/$realisation/CCDF/ 
  done
done

