#!/bin/bash

run_dir=$1 #/home/nesi00213/RunFolder/Cybershake/v17p8/Runs - This allows us to change between simulation datasets (eg to v17p9)
list_runs=`cat $2` # A list containing all run (fault) names
csv=${3:-MB2013_Total_occupied_private_dwellings.csv}

cd /home/nicole # This is where we find the other scripts # THIS ALSO NEEDS TO BE REDIRECTED

# The primary loop, going through one fault name at a time
for run_name in $list_runs
do
    for realisation_path in `find  $run_dir/$run_name/Impact/Liquefaction/ -type d -name $run_name"_HYP*"` #Pull out the filepath to the directory for specific realisation of the chosen fault
    do
        realisation=$(basename $realisation_path) # This creates a variable with the realisation name (eg AlpineF2K_HYP01-03_S1254)
        python /home/fordw/Scripts/CCDF_scripts_and_plots/PopnTest.py $realisation_path/*zhu_2016_general_probability_nz-specific-vs30.xyz MB2013_GV_Clipped/MB2013_GV_Clipped.shp $csv
        python /home/fordw/Scripts/CCDF_scripts_and_plots/PopnTest.py $realisation_path/*zhu_2016_general_probability_topo-based-vs30.xyz MB2013_GV_Clipped/MB2013_GV_Clipped.shp $csv
        python /home/fordw/Scripts/CCDF_scripts_and_plots/PopnTest.py $realisation_path/*zhu_2016_coastal_probability_nz-specific-vs30.xyz MB2013_GV_Clipped/MB2013_GV_Clipped.shp $csv
        python /home/fordw/Scripts/CCDF_scripts_and_plots/PopnTest.py $realisation_path/*zhu_2016_coastal_probability_topo-based-vs30.xyz MB2013_GV_Clipped/MB2013_GV_Clipped.shp $csv
        python /home/fordw/Scripts/CCDF_scripts_and_plots/PopnTest.py $run_dir/$run_name/Impact/Landslide/$realisation/*probability.xyz MB2013_GV_Clipped/MB2013_GV_Clipped.shp $csv
    done
done

