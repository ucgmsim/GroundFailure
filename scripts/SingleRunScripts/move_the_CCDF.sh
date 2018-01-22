#!/bin/bash

# This is a single run script designed to move a bunch of CCDF .png files from one folder to a nested folder within that.
# This was written because of an error in CCDF_regional.py at the time of its conception
# There are no inputs to this script

# Written by Luke Longworth on 16/01/2018

list_runs=`cat /home/nesi00213/RunFolder/Cybershake/v17p8/temp/list_runs_v17p8` # Create a list of the names of the faults in the affected structure (v17p8)

for run_name in $list_runs #Picks a fault from the list you input (e.g. AlpineF2K)
do
  for realisation_path in `find  /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/$run_name/GM/Validation/ -type d -name ""$run_name"_HYP*"` #Pull out the filepath to the directory for specific realisation of the chosen fault
  do
    realisation=$(basename $realisation_path) # Returns the realisation name (eg AlpineF2K_HYP01-03_S1254) rather than the whole filepath
    mv /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/$run_name/Impact/Landslide/$realisation/Regional_CCDF* /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/$run_name/Impact/Landslide/$realisation/CCDF/ # Moves the relevant files to the correct folder. Currently, this code does not check if they exist before trying to move them, so error messages pop up in the window when the files don't exist
  done
done

