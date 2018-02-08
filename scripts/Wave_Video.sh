#!/bin/bash

# This code steps through each realisation and creates a video (.m4v) file showing the wave propagation of an earthquake.
# This produces the 2D birds' eye view movie

# Inputs: 1) A filepath to the runs directory within which each fault is a subfolder (must be full filepath, not using shortcuts like . or ..
#         2) A file that contains all the fault names. This will need to be written for each set of cybershake runs (eg. v17p8)
#            These can be found at /home/nesi00213/RunFolder/Cybershake/v17p8/temp/list_runs_v17p8 or equivalent for v17p9
#            The filepath should be provided such that `cat $2` outputs a list of strings

# Usage: bash /home/nesi00213/groundfailure/scripts/Wave_Video.sh /home/nesi00213/Runfolder/Cybershake/v17p8/Runs /home/nesi00213/Runfolder/Cybershake/v17p8/temp/list_runs_v17p8 16

# The code defaults to running 8 frames simultaneously, but the third input can be anywhere between 1 and 32. It is recommended to use 8 to 16.

# This code was written on 08/02/2018 by Luke Longworth
# Contact at luke.longworth.nz@gmail.com

run_dir=$1
list_runs=`cat $2`
number_of_frames=${3:-8}

for run in $list_runs
do
  cd $run_dir/$run/GM/Sim/Data/$run # Move to the folder of the next fault
  python /home/nesi00213/qcore/plot/plot_ts.py $number_of_frames # Run plot_ts.py with the specified number of frames rendering simultaneously
  mkdir $run_dir/$run/Impact/GM/ # Make the output directory
  name=$run"_2D_animation.m4v" # Create filename
  mv $run_dir/$run/animation.m4v $run_dir/$run/Impact/GM/$name # Move the movie into a more appropriate folder and rename it to a more descriptive title
done

