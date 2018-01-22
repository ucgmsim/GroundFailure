#!/bin/bash

run_dir=$1 #/home/nesi00213/RunFolder/Cybershake/v17p8/Runs - This allows us to change between simulation datasets (eg to v17p9)
list_runs=`cat $2` #A relevant list is called list_runs_v17p8 in the run_dir/../temp

cd $run_dir/..
dataset=$(basename $PWD)
mkdir /home/lukelongworth/grids/$dataset
cd /home/nesi00213/post-processing/scripts/

for run_name in $list_runs #Picks a fault from the list you input (e.g. AlpineF2K)
do
  for realisation_path in `find  $run_dir/$run_name/GM/Validation/ -type d -name ""$run_name"_HYP*"` #Pull out the filepath to the directory for specific realisation of the chosen fault
  do
    realisation=$(basename $realisation_path) #Pull out the name of the realisation without the rest of the filepath
    #Run the csv conversion script
    python export_lonlat_pgv2csv.py $realisation_path/Data/database.db $run_dir/$run_name/GM/Sim/Data/$run_name/$realisation
    #Produce the grid.xml file
    mag=`python /home/lukelongworth/GroundFailure/scripts/get_mag.py $realisation_path` # Get the magnitude of the rupture
    depth=`python /home/lukelongworth/GroundFailure/scripts/get_depth.py $realisation_path` # Get the depth of the rupture
    corners=`python /home/lukelongworth/GroundFailure/scripts/get_corners.py $run_dir $run_name $realisation` #Get the corners of the surface
    python /home/nesi00213/groundfailure/haz_analysis/grd2grid.py $run_dir/$run_name/GM/Sim/Data/$run_name/$realisation/lonlatpgv*.csv $realisation $run_dir/$run_name/GM/Sim/Data/$run_name/$realisation -m $mag -d $depth -c $corners --dx 1k
    cp $run_dir/$run_name/GM/Sim/Data/$run_name/$realisation/grid.xml /home/lukelongworth/grids/$dataset/grid_$realisation.xml
  done
done

