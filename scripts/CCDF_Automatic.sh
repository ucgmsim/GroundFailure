#!/bin/bash

# This script was written by Luke Longworth in Jan 2018 to work with the code written by Ford Wagner

# Inputs: 1) A filepath to the runs directory within which each fault is a subfolder (must be full filepath, not using shortcuts like . or ..
#         2) A file that contains all the fault names. This will need to be written for each set of cybershake runs (eg. v17p8)
#            These can be found at /home/nesi00213/RunFolder/Cybershake/v17p8/temp/list_runs_v17p8 or equivalent for v17p9
#            The filepath should be provided such that `cat $2` outputs a list of strings

# Usage: bash /home/nesi00213/groundfailure/scripts/CCDF_Automatic.sh /home/nesi00213/Runfolder/Cybershake/v17p8/Runs /home/nesi00213/Runfolder/Cybershake/v17p8/temp/list_runs_v17p8

# Name the inputs
run_dir=$1 #/home/nesi00213/RunFolder/Cybershake/v17p8/Runs - This allows us to change between simulation datasets (eg to v17p9)
list_runs=`cat $2` # A list containing all run (fault) names

cd /home/nesi00213/groundfailure/scripts/ # This is where we find the other scripts

for run_name in $list_runs
do
  rm $run_dir/$run_name/Impact/Landslide/CCDF/*.png
  rm $run_dir/$run_name/Impact/Liquefaction/CCDF/*.png
  for realisation_path in `find  $run_dir/$run_name/Impact/Liquefaction/ -type d -name ""$run_name"_HYP*"` #Pull out the filepath to the directory for specific# realisation of the chosen fault
  do
        realisation=$(basename $realisation_path) # This creates a variable with the realisation name (eg AlpineF2K_HYP01-03_S1254)
        rm $realisation_path/CCDF/*.png
        rm $run_dir/$run_name/Impact/Landslide/$realisation/CCDF/*.png
  done
done


# The primary loop, going through one fault name at a time
for run_name in $list_runs
do
    # Firstly create the relevant folders to save the results to
    if [ ! -e $run_dir/$run_name/Impact/Liquefaction/CCDF/ ]; then
      mkdir $run_dir/$run_name/Impact/Liquefaction/CCDF/
    fi
    if [ ! -e $run_dir/$run_name/Impact/Landslide/CCDF/ ]; then
      mkdir $run_dir/$run_name/Impact/Landslide/CCDF/
    fi
    # Enter the secondary loop
    for realisation_path in `find  $run_dir/$run_name/Impact/Liquefaction/ -type d -name ""$run_name"_HYP*"` #Pull out the filepath to the directory for specific realisation of the chosen fault
    do
        realisation=$(basename $realisation_path) # This creates a variable with the realisation name (eg AlpineF2K_HYP01-03_S1254)
    
        # Create the relevant output directories
        if [ ! -e $realisation_path/$realisation/CCDF/ ]; then
          mkdir $realisation_path/$realisation/CCDF/
        fi
        if [ ! -e $realisation_path/../../Landslide/$realisation/CCDF/ ]; then
          mkdir $realisation_path/../../Landslide/$realisation/CCDF/
        fi
    
        # Run the relevant files
        python CCDF_regional_popn.py $realisation_path/*zhu_2016_coastal_probability_n*
        python CCDF_regional_popn.py $realisation_path/*zhu_2016_coastal_probability_t*
        python CCDF_regional_popn.py $realisation_path/*zhu_2016_general_probability_n*
        python CCDF_regional_popn.py $realisation_path/*zhu_2016_general_probability_t*
        python CCDF_regional_popn.py $run_dir/$run_name/Impact/Landslide/$realisation/*probability.xyz --datatype landslide
        
        python CCDF_regional_popn.py $realisation_path/*zhu_2016_coastal_probability_n* --xAxis pop
        python CCDF_regional_popn.py $realisation_path/*zhu_2016_coastal_probability_t* --xAxis pop
        python CCDF_regional_popn.py $realisation_path/*zhu_2016_general_probability_n* --xAxis pop
        python CCDF_regional_popn.py $realisation_path/*zhu_2016_general_probability_t* --xAxis pop
        python CCDF_regional_popn.py $run_dir/$run_name/Impact/Landslide/$realisation/*probability.xyz --xAxis pop --datatype landslide
        
        python CCDF_regional_popn.py $realisation_path/*zhu_2016_coastal_probability_n* --xAxis dwell
        python CCDF_regional_popn.py $realisation_path/*zhu_2016_coastal_probability_t* --xAxis dwell
        python CCDF_regional_popn.py $realisation_path/*zhu_2016_general_probability_n* --xAxis dwell
        python CCDF_regional_popn.py $realisation_path/*zhu_2016_general_probability_t* --xAxis dwell
        python CCDF_regional_popn.py $run_dir/$run_name/Impact/Landslide/$realisation/*probability.xyz --xAxis dwell --datatype landslide
    done
done

