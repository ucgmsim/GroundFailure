#!/bin/bash

# This script takes a .txt file such as the ones produced by Cybershake and converts them to a collated .csv file with information on expected effect over time

# Usage and example:
# bash /home/nesi00213/groundfailure/scripts/hazard_prob_plot.sh /path/to/folder/containing/.txtfile "Name of .txt file" Number_of_years_over_which_to_analyse list,of,probabilities,from,largest,to,smallest The_ini_file_that_the_analysis_will_use.ini
# bash /home/nesi00213/groundfailure/scripts/hazard_prob_plot.sh /home/lukelongworth/Test_folder HazMapData.txt 50 0.8,0.5,0.2,0.1,0.08,0.06,0.04,0.02,0.01,0.005,0.002 zhu_2016_general_probability_nz-specific-vs30.ini

# Defaults: $1 and $2 are compulsory inputs, $3 will default to 50, $4 will default to 0.8,0.5,0.25,0.1,0.08,0.06,0.04,0.02,0.01,0.005, $5 will default to zhu_2016_general_probability_nz-specific-vs30.ini

# Other $5 config files you can choose are:
#    jessee_2017_probability.ini
#    zhu_2016_coastal_probability_nz-specific-vs30.ini
#    zhu_2016_coastal_probability_topo-based-vs30.ini
#    zhu_2016_general_probability_nz-specific-vs30.ini
#    zhu_2016_general_probability_topo-based-vs30.ini
# With the jessee model being landslide and the zhu model being liquefaction

# This script was written by Luke Longworth in December 2017

# Initialise variables
source_folder=$1 #"/home/lukelongworth"
source_file=$2 # "HazCurveResults.txt" Should be in source_folder
years=${3:-50.0} # 50
probabilities=${4:-0.8,0.5,0.25,0.1,0.08,0.06,0.04,0.02,0.01,0.005} #0.8,0.5,0.25,0.1,0.08,0.06,0.04,0.02,0.01,0.005
ini=${5:-jessee_2017_probability.ini} #This enables you to change the config file to use different liquefaction models or switch to landslide

# Check whether we are dealing with liquefaction or landslides
if [[ $ini == *"zhu"* ]]; then
  situation="liq"
else
  situation="ls"
fi

# Initialise directories
mkdir $source_folder/HazMapData
mkdir $source_folder/HazMapData/xyz

# Firstly produce a csv
# This step reads the data from the source file and organises it into a neat, easy to digest format.
# Each probability outlined above will produce an individual .txt file
cd $source_folder
python /home/nesi00213/groundfailure/scripts/haz_curve_prob_export.py $source_file -i $source_folder -p $probabilities -y $years -o $source_folder/HazMapData
echo The .txt files have been produced from the master file $source_file

cd HazMapData

# Then start stepping through each probability .txt file produced in the previous step
for f in pgv_*.txt
do
  echo Take $f as the probability
  # Take this .txt file and runs grd2grid.py
  python /home/nesi00213/dev/groundfailure/haz_analysis/grd2grid.py $source_folder/HazMapData/$f $f $source_folder/HazMapData/grids/
  echo produced the grid.xml file

  # The configuration file we need is different based on whether it is liquefaction or landslide
  # Runs the gfail script on the grid.xml file
  if [[ $situation == "liq" ]]; then
    python3 /usr/bin/gfail $ini $source_folder/HazMapData/grids/grid.xml --set-bounds 'zoom, pgv, 0' --hdf5 -o $source_folder/HazMapData/grids -c /home/nesi00213/groundfailure/config/ -d /home/nesi00213/groundfailure/liquefaction_model/ 
  else
    python3 /usr/bin/gfail $ini $source_folder/HazMapData/grids/grid.xml --set-bounds 'zoom, pgv, 0' --hdf5 -o $source_folder/HazMapData/grids -c /home/nesi00213/groundfailure/config/ -d /home/nesi00213/groundfailure/landslide_model/
  fi
  echo produced the h5 files
  
  # Run gen_gf_surface.py on the h5 files
  python /home/nesi00213/groundfailure/gen_gf_surface.py -type $situation -t '' -o $source_folder/HazMapData/xyz/$f.xyz $source_folder/HazMapData/grids/$f/*.hdf5 --keep-nans
  echo produced the xyz files
  
  # Save the grid.xml file to a new location so that it doesn't get saved over in the next iteration
  cp $source_folder/HazMapData/grids/grid.xml $source_folder/HazMapData/grids/$f/
  echo We have finished analysing the probability of $f

done

# Clean up the folder by removing the last grid.xml file that didn't get saved over
rm $source_folder/HazMapData/grids/grid.xml

# jollate all of the probability files together and integrate them.
python /home/nesi00213/groundfailure/scripts/collate.py -i $source_folder/HazMapData/xyz -o $source_folder/final_collation.csv # output into a file in the output directory

echo Produced collation

# Now plot it using plot_stations.py
# The inputs are different depending on whether it is liq or ls
# Firstly we pull out the first 3 columns of the master file and save this to a new file
# Secondly we add a relevant header with useful information
# Thirdly we run plot_stations.py on this file
# Then we tidy up: Rename the graph so we know what it is, and we delete the obsolete csv file
if [[ $situation == "liq" ]]; then
  awk {'print $1,$2,$3'} $source_folder/final_collation.csv > $source_folder/liq_hazard_prob.csv # Take the first three columns of the data and ignore the rest
  cat /home/nesi00213/groundfailure/scripts/Data/plot_header_liq.txt $source_folder/liq_hazard_prob.csv > $source_folder/liq_hazard_prob.xyz # Add a header for use in plotting
  python /home/nesi00213/qcore/plot/plot_stations.py $source_folder/liq_hazard_prob.xyz --out_dir $source_folder # Plot the results
  mv $source_folder/c000.png $source_folder/liq_hazard_prob.png # Tidy the results up (rename the graph and remove the obsolete file)
  rm $source_folder/liq_hazard_prob.csv
else
  awk {'print $1,$2,$3'} $source_folder/final_collation.csv > $source_folder/ls_hazard_prob.csv # Take the first three columns of the data and ignore the rest
  cat /home/nesi00213/groundfailure/scripts/Data/plot_header_ls.txt $source_folder/ls_hazard_prob.csv > $source_folder/ls_hazard_prob.xyz # Add a header for use in plotting
  python /home/nesi00213/qcore/plot/plot_stations.py $source_folder/ls_hazard_prob.xyz --out_dir $source_folder # Plot the results
  mv $source_folder/c000.png $source_folder/ls_hazard_prob.png # Tidy the results up (rename the graph and remove the obsolete file)
  rm $source_folder/ls_hazard_prob.csv
fi
