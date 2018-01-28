#!/bin/bash

# This script automatically creates a folder structure with all relevant visual media nested in relevant folders
# This was designed with the USER programme website in mind

# This was written by Luke Longworth on 15/01/2018

# Input: 1) OPTIONAL: Output directory

# Usage and example: 
# bash /path/to/file/collate_website.sh /path/to/output/directory
# bash /home/nesi00213/groundfailure/scripts/collate_website.sh .

out_dir=${1:-'.'}
if [[ $out_dir == '.' ]]; then
  out_dir=`pwd`
fi

# Create the home folder
mkdir $out_dir/website_data/

# Get the relevant text file for gen_Fault_Info.txt
cp /home/nesi00213/groundfailure/scripts/Data/NZ_FLTmodel_2010.txt $out_dir 

# Set up the list of different models 
list1=('v17p8' 'v17p9')

# Start with v17p8, then move on to v17p9

for i in {0,1}
do
  run=${list1[i]}
  # Create the relevant folder and variable name
  list='list_runs_'$run
  mkdir $out_dir/website_data/$run
  
  # Step through the faults one by one
  for run_name in `cat /home/nesi00213/RunFolder/Cybershake/$run/temp/$list`
  do
    run_dir='/home/nesi00213/RunFolder/Cybershake/'$run'/Runs' # Create this useful variable (common in other Luke Longworth scripts)
    mkdir $out_dir/website_data/$run/$run_name # Create the next directory
    cd $run_dir/$run_name/GM/Validation # Go to the relevant folder 
    ls -1 -d *HYP* > $out_dir/website_data/$run/$run_name/realisation_list.txt # Print a list of the realisations to a new file in our folder structure
    # Now enter a tertiary for loop: realisations 
    for realisation in `cat $out_dir/website_data/$run/$run_name/realisation_list.txt`
    do
      # Make the relevant directories
      mkdir $out_dir/website_data/$run/$run_name/$realisation/
      mkdir $out_dir/website_data/$run/$run_name/$realisation/PNGs/
      mkdir $out_dir/website_data/$run/$run_name/$realisation/videos/
      # Copy the files across. At this stage, the first several files cannot be found reliably and so they are currently copying a placeholder
      cp /home/lukelongworth/Placeholder.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/MMI.png # cp MMI map
      cp /home/lukelongworth/Placeholder.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/PGA.png # cp PGA map
      cp /home/lukelongworth/Placeholder.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/PGV.png # cp PGV map
      cp /home/lukelongworth/Placeholder.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/PopulationCCDF.png # cp Pop CCDF
      cp /home/lukelongworth/Placeholder.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/GMTmaps.png # cp GMT maps for everything
      cp /home/lukelongworth/Placeholder.png $out_dir/website_data/$run/$run_name/$realisation/videos/WaveVideo.mp4 # cp 2D Wave Propagation video
      cp /home/lukelongworth/Placeholder.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/StateHighwayCCDF.png # cp SH CCDF
      cp /home/lukelongworth/Placeholder.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/DwellingCCDF.png # cp Dwelling CCDF
      cp /home/lukelongworth/Placeholder.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/PowerCCDF.png # cp Power Grid CCDF
      # The next four files check for the file and if it does not exist they also copy the placeholder
      if [ -f /home/nesi00213/RunFolder/Cybershake/$run/Runs/$run_name/Impact/Liquefaction/$realisation/*c-vs30_probability_general.png ]; then
        cp /home/nesi00213/RunFolder/Cybershake/$run/Runs/$run_name/Impact/Liquefaction/$realisation/*c-vs30_probability_general.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/LiquefactionProbability.png
      else
        cp /home/lukelongworth/Placeholder.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/LiquefactionProbability.png
      fi
      if [ -f /home/nesi00213/RunFolder/Cybershake/$run/Runs/$run_name/Impact/Landslide/$realisation/*probability_.png ]; then
        cp /home/nesi00213/RunFolder/Cybershake/$run/Runs/$run_name/Impact/Landslide/$realisation/*probability_.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/LandslideProbability.png
      else
        cp /home/lukelongworth/Placeholder.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/LandslideProbability.png
      fi
      if [ -f /home/nesi00213/RunFolder/Cybershake/$run/Runs/$run_name/Impact/Liquefaction/$realisation/CCDF/Regional*general_probability_nz-specific-vs30.png ]; then
        cp /home/nesi00213/RunFolder/Cybershake/$run/Runs/$run_name/Impact/Liquefaction/$realisation/CCDF/Regional*general_probability_nz-specific-vs30.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/LiquefactionCCDF.png
      else
        cp /home/lukelongworth/Placeholder.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/LiquefactionCCDF.png
      fi
      if [ -f /home/nesi00213/RunFolder/Cybershake/$run/Runs/$run_name/Impact/Landslide/$realisation/CCDF/*.png ]; then
        cp /home/nesi00213/RunFolder/Cybershake/$run/Runs/$run_name/Impact/Landslide/$realisation/CCDF/*.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/LandslideCCDF.png
      else
        cp /home/lukelongworth/Placeholder.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/LandslideCCDF.png
      fi
    done
  done
  # Run yni23's script that extracts mag, dep, hypocentre and fault trace.
  cd $out_dir
  python /home/nesi00213/groundfailure/scripts/gen_Fault_Info.py $run $out_dir
done

# Clean up
rm $out_dir/NZ_FLTmodel_2010.txt

cd $out_dir
zip -r website_data .