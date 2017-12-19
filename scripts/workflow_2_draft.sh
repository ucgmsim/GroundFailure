# The purpose of this script is:

# 1) Takes /home/jam335/hazard_liq/HazCurveResults.txt and runs /home/nesi00213/dev/cybershake_postprocessing/post-processing/haz_curve_prob_extract.py
#    This changes the ugly horizontal space-separated lists into a beautiful, easy to read, vertical vector giving a lon-lat-PGV
#    These are found in /home/jam335/hazard_liq/HazMapData/ just listed randomly there
# 2) Runs /home/nesi00213/groundfailure/haz-analysis/grd2grid.py on the .txt files that we just produced (essentially the same as a csv)
#    These are located in /home/jam335/hazard_liq/HazMapData/grids/ in nested folders based on probability
# 3) Use the steps inside plot_liq and plot_ls to produce xyz files to a specific grid.xml file
#    These save in the same folder as the grid.xml files they were made from
# 4) Move all of these .xyz files into their own folder /home/jam335/hazard_liq/HazMapData/grids/xyz/
# 5) Run collate.py found in /home/jam335/hazard_liq/HazMapData/grids/xyz/

#!/bin/bash

# This script takes a badly formatted .txt file and turns it into a beautiful csv file

# Let's talk about variables
source_folder=$1 #"/home/lukelongworth"
source_file=$2 # "HazCurveResults.txt" Should be in source_folder
years=${3:-50.0} # 50
probabilities=${4:-0.8,0.5,0.25,0.1,0.08,0.06,0.04,0.02,0.01,0.005} #0.8,0.5,0.25,0.1,0.08,0.06,0.04,0.02,0.01,0.005
ini=${5:-zhu_2016_general_probability_nz-specific-vs30.ini}

echo "The first input is the source folder:" $source_folder
echo "The second input is the source file:" $source_file
echo "The third input is the number of years over which we want to analyse:" $years
echo "The fourth input is the list of probabilities:" $probabilities
echo "The fifth and final input is the .ini file we want to use:" $ini

mkdir $source_folder/HazMapData
mkdir $source_folder/HazMapData/xyz

echo Created directories $source_folder/HazMapData and $source_folder/HazMapData/xyz

# Firstly produce a csv
cd $source_folder
echo Moved to $source_folder
cp /home/lukelongworth/non_uniform_whole_nz-hh400.ll $source_folder
echo Copied across non_uniform_whole_nz-hh400.ll
python /home/lukelongworth/GroundFailure/scripts/haz_curve_prob_export_2.py -i $source_folder -p $probabilities -y $years -o $source_folder/HazMapData $source_file  
echo The .txt files have been produced from the master file $source_file
cd HazMapData
echo Navigated to the subdirectory HazMapData
# Then a for loop
echo "Enter the FOR LOOP"
for f in pgv_*.txt
do
  echo "In this loop we are concerned with" $f
  # Then take this csv and runs grd2grid
  python /home/nesi00213/groundfailure/haz_analysis/grd2grid.py $source_folder/HazMapData/$f $f $source_folder/HazMapData/grids/
  echo produced the grid.xml file
  # Then we take this grid.xml file and produce an xyz file using the same files that we use in the plot_liq process??? 
  # I need to ask Jason about this one

  # gfail
  # gen_gf_surface.py

  python3 /usr/bin/gfail $ini $source_folder/HazMapData/grids/grid.xml --set-bounds 'zoom, pgv, 0' --hdf5 -o $source_folder/HazMapData/grids -c /home/nesi00213/groundfailure/config/ -d /home/nesi00213/groundfailure/liquefaction_model/
  echo produced the h5 files
  #NOTES: Which .ini files do I use? Do I need to write a flagging system in a copied+edited script that automatically pulls out the correct one for each scenario?
  #       What are the --data-files? I have no idea what to put here

  python /home/nesi00213/groundfailure/gen_gf_surface.py -t '' -o $source_folder/HazMapData/xyz/$f.xyz $source_folder/HazMapData/grids/$f/*.hdf5 --keep-nans
  echo produced the xyz files
  echo We have finished analysing $f

done

echo "The FOR LOOP is finished!"

cp /home/lukelongworth/HazMapData/xyz/collate2.py $source_folder/HazMapData/xyz/
echo Copied the collate file over to the relevant folder
cd $source_folder/HazMapData/xyz/
python $source_folder/HazMapData/xyz/collate2.py -p $probabilities > $source_folder/final_collation.csv
echo "The script is finished praise the lord"

