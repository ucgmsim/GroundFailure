# This is a modified version of cybershake_run_liqls.sh developed when there was an error in plot_ls.py 
# It takes the same inputs but doesn't check to see if a run is complete
# It just produces the relevant outputs for landslides without reproducing the csv, xml or liq plots
# It really shouldn't need to be run unless there is an issue with all landslide plots

run_dir=$1 #/home/nesi00213/RunFolder/Cybershake/v17p8/Runs - This allows us to change between simulation datasets (eg to v17p9)
list_runs=`cat $2` #A relevant list is called list_runs_v17p8 in the run_dir

cd /home/nesi00213/dev/post-processing/scripts/ #Allows export_lonlat_pgv2csv.py to run

for run_name in $list_runs #Picks a fault from the list you input (e.g. AlpineF2K)
do
  for realisation_path in `find  $run_dir/$run_name/GM/Validation/ -type d -name ""$run_name"_HYP*"` #Pull out the filepath to the directory for specific realisation of the chosen fault
  do
    realisation=$(basename $realisation_path) #Pull out the name of the realisation without the rest of the filepath
    #Run the landslide calcs
    python /home/nesi00213/groundfailure/plot_ls.py $run_dir/$run_name -r $realisation
  done
done
