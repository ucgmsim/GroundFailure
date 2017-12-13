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
the_ugly_folder="/home/jam335/hazard_liq/"
the_ugly_file="HazCurveResults.txt"
probabilities=[0.005, 0.01, 0.02, 0.05, 0.1, 0.5, 0.8]

# Firstly produce a csv
python /home/nesi00213/dev/cybershake_postprocessing/post-processing/haz_curve_prob_extract.py $the_ugly_folder/$the_ugly_file $probabilities $the_ugly_folder
# TODO: Edit this file (make a copy) so that this script takes in a filename (or filepath??), a set of probabilities to order into bins, and an output directory

# Then a for loop
in a for loop
do
# Then take this csv and runs grd2grid
python /home/nesi00213/groundfailure/haz-analysis/grd2grid.py $the_ugly_folder/$pretty_file some_sort_of_file_name $the_ugly_folder

# Then we take this grid.xml file and produce an xyz file using the same files that we use in the plot_liq process??? 
# I need to ask Jason about this one

cp $outputxyz $the_ugly_folder/xyz/

done

collate.py