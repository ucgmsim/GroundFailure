#!/bin/bash

# This code steps through each realisation and creates a series of complementary cumulative distribution functions, CCDFs
# It makes use of the python2 scripts in /home/nesi00213/groundfailure/scripts named 'CCDF_regional.py' 'All_models.py' and 'All_realisations.py'

# This script was written by Luke Longworth in Jan 2018 to work with the code written by Ford Wagner

# Inputs: 1) A filepath to the runs directory within which each fault is a subfolder
#         2) A file that contains all the fault names. This will need to be written for each set of cybershake runs (eg. v17p8)

# Usage: bash /home/lukelongworth/GroundFailure/scripts/CCDF_Automatic.sh /home/nesi00213/Runfolder/Cybershake/v17p8/Runs /home/nesi00213/Runfolder/Cybershake/v17p8/temp/list_runs_v17p8

# Name the inputs
run_dir=$1 #/home/nesi00213/RunFolder/Cybershake/v17p8/Runs - This allows us to change between simulation datasets (eg to v17p9)
list_runs=`cat $2` # A list containing all run (fault) names

cd /home/fordw/Scripts/CCDF_scripts_and_plots/ # This is where we find the other scripts # THIS ALSO NEEDS TO BE REDIRECTED

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
    
    # Then run the script
    # This doesn't need an input of specific realisations so we run it before we get into the secondary for loop
    # It runs four times, creating two graphs each for liquefaction and landslide; one that plots the detailed realisation and one that plots the mean
    python All_realisations.py $run_dir/$run_name
    python All_realisations.py $run_dir/$run_name --datatype ls
    python All_realisations.py $run_dir/$run_name --grey grey
    python All_realisations.py $run_dir/$run_name --datatype ls --grey grey
    
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
        python CCDF_regional.py $realisation_path/*zhu_2016_coastal_probability_n*
        python CCDF_regional.py $realisation_path/*zhu_2016_coastal_probability_t*
        python CCDF_regional.py $realisation_path/*zhu_2016_general_probability_n*
        python CCDF_regional.py $realisation_path/*zhu_2016_general_probability_t*
        python CCDF_regional.py $run_dir/$run_name/Impact/Landslide/$realisation/*probability.xyz 
    
        python All_models.py $realisation_path/

    done
done

