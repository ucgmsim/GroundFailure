#!/bin/bash 

# Takes a list of all realisations and produces the .bil files for susceptibility
# Inputs: 1) Filepath to the directory of choice (e.g. /home/../v17p8/Runs)
#         2) A list of all relevant runs. Just a simple text file.
# Outputs: A bunch of .bil files that can be used more easily in GIS

run_dir=$1
list_runs=`cat $2`

for run_name in $list_runs
do
  for realisation_path in `find  $run_dir/$run_name/GM/Sim/Data/$run_name -type d -name ""$run_name"_HYP*"`
  do
    python3 /usr/bin/gfail /home/nesi00213/groundfailure/config/jessee_2017_probability.ini $realisation_path/grid.xml --set-bounds 'zoom, pgv, 0' --hdf5 -o /home/lukelongworth/BILs/Prob/Landslide/ -c /home/nesi00213/groundfailure/config -d /home/nesi00213/groundfailure/landslide_model --gis
  done
done

