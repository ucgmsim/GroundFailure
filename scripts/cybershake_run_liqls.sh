#!/bin/bash

# This code steps through each realisation and produces the probability maps for liquefaction and landslides.
# Inputs: 1) A filepath to the runs directory within which each fault is a subfolder (must be full filepath, not using shortcuts like . or ..
#         2) A file that contains all the fault names. This will need to be written for each set of cybershake runs (eg. v17p8)
#            These can be found at /home/nesi00213/RunFolder/Cybershake/v17p8/temp/list_runs_v17p8 or equivalent for v17p9
#            The filepath should be provided such that `cat $2` outputs a list of strings

# This code was written by Luke Longworth on 28th November 2017

# Usage and example:
# bash /path/to/file/cybershake_run_liqls.sh /path/to/run/folder/ /path/to/list/runs
# bash /home/nesi00213/groundfailure/scripts/cybershake_run_liqls.sh /home/nesi00213/RunFolder/Cybershake/v17p8/Runs /home/nesi00213/RunFolder/Cybershake/v17p8/temp/list_runs_v17p8

# Checks if you have enough inputs
if [[ $# -lt 2 ]]; then
    echo "please provide a path to runs and list"
    exit 1
fi

# Name the inputs
run_dir=$1 #/home/nesi00213/RunFolder/Cybershake/v17p8/Runs - This allows us to change between simulation datasets (eg to v17p9)
list_runs=`cat $2` #A relevant list is called list_runs_v17p8 in the run_dir/../temp

cd /home/nesi00213/post-processing/scripts/ #Allows export_lonlat_pgv2csv.py to run. This script must be run from its home folder or it cannot find the relevant files

# Track the realisations that have been completed
if [ -e $run_dir/../temp/completed_liqls.log]; then 
    completed_liqls_list=`cat $run_dir/../temp/completed_liqls.log` 
else
    echo > $run_dir/../temp/completed_liqls.log
    completed_liqls_list=`cat $run_dir/../temp/completed_liqls.log`
fi

for run_name in $list_runs #Steps through faults from the list you input (e.g. AlpineF2K)
do
  for realisation_path in `find  $run_dir/$run_name/GM/Validation/ -type d -name ""$run_name"_HYP*"` #Pull out the filepath to the directory for specific realisation of the chosen fault
  do
    realisation=$(basename $realisation_path) #Pull out the name of the realisation without the rest of the filepath
    [[ $completed_liqls_list =~ (^|[[:space:]])$realisation($|[[:space:]]) ]] && continue #If the realisation has been done, choose the next one
    #Run the csv conversion script. Some folders have database.db and others have database.json, while some further have both. This if-else allows the programme to run this step only once and not get confused at the different types. 
    if [[ -e $realisation_path/Data/database.db ]]; then
      python export_lonlat_pgv2csv.py $realisation_path/Data/database.db $run_dir/$run_name/GM/Sim/Data/$run_name/$realisation
    else
      python export_lonlat_pgv2csv.py $realisation_path/Data/database.json $run_dir/$run_name/GM/Sim/Data/$run_name/$realisation
    fi
    #Produce the grid.xml file
    mag=`python /home/lukelongworth/GroundFailure/scripts/get_mag.py $realisation_path` # Get the magnitude of the rupture
    depth=`python /home/lukelongworth/GroundFailure/scripts/get_depth.py $realisation_path` # Get the depth of the rupture
    corners=`python /home/lukelongworth/GroundFailure/scripts/get_corners.py $run_dir $run_name $realisation` #Get the corners of the surface
    python /home/nesi00213/groundfailure/haz_analysis/grd2grid.py $run_dir/$run_name/GM/Sim/Data/$run_name/$realisation/lonlatpgv_*.csv $realisation $run_dir/$run_name/GM/Sim/Data/$run_name/$realisation -m $mag -d $depth -c $corners #Run the script using the default resolution of 2k
    #Run the landslide calcs
    python /home/nesi00213/groundfailure/plot_ls.py $run_dir/$run_name -r $realisation
    #Run the liquefaction calcs
    python /home/nesi00213/groundfailure/plot_liq.py $run_dir/$run_name -r $realisation
    echo $realisation >> $run_dir/../temp/completed_liqls.log #Add the now-completed realisation to the list of completed realisations
  done
done
