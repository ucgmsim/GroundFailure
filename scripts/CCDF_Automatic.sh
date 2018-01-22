#!/bin/bash

# This code steps through each realisation and creates the CCDF for liquefaction
# Inputs: 1) A filepath to the runs directory within which each fault is a subfolder
#         2) A file that contains all the fault names. This will need to be written for each set of cybershake runs (eg. v17p8)

# Usage: bash /home/lukelongworth/GroundFailure/scripts/CCDF_Automatic.sh /home/nesi00213/Runfolder/Cybershake/v17p8/Runs /home/nesi00213/Runfolder/Cybershake/v17p8/temp/list_runs_v17p8

# Name the inputs
run_dir=$1 #/home/nesi00213/RunFolder/Cybershake/v17p8/Runs - This allows us to change between simulation datasets (eg to v17p9)
list_runs=`cat $2`

cd /home/fordw/GroundFailure/scripts/

for run_name in $list_runs
do
    mkdir $run_dir/$run_name/Impact/Liquefaction/CCDF/
    mkdir $run_dir/$run_name/Impact/Landslide/CCDF/
    
    python All_realisations.py $run_dir/$run_name
    python All_realisations.py $run_dir/$run_name --datatype ls
    python All_realisations.py $run_dir/$run_name --grey grey
    python All_realisations.py $run_dir/$run_name --datatype ls --grey grey
    
    for realisation_path in `find  $run_dir/$run_name/Impact/Liquefaction/ -type d -name ""$run_name"_HYP*"` #Pull out the filepath to the directory for specific realisation of the chosen fault
    do
        realisation=$(basename $realisation_path)
    
        mkdir $realisation_path/$realisation/CCDF/
        mkdir $realisation_path/../../Landslide/$realisation/CCDF/
    
        python CCDF_regional.py $realisation_path/*zhu_2016_coastal_probability_n*
        python CCDF_regional.py $realisation_path/*zhu_2016_coastal_probability_t*
        python CCDF_regional.py $realisation_path/*zhu_2016_general_probability_n*
        python CCDF_regional.py $realisation_path/*zhu_2016_general_probability_t*
        python CCDF_regional.py $run_dir/$run_name/Impact/Landslide/$realisation/*probability.xyz 
    
        python All_models.py $realisation_path/

    done
done

