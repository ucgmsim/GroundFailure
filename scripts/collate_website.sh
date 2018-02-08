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

# Get the relevant text file for gen_Fault_Info.py
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
      
      # MMI
      if [ -f /home/nesi00213/RunFolder/Cybershake/$run/Runs/$run_name/GM/Validation/$realisation/Data/comparison_plots/nonuniform_plot_comparison_map_MMI_$realisation/c000.png ]; then
        cp /home/nesi00213/RunFolder/Cybershake/$run/Runs/$run_name/GM/Validation/$realisation/Data/comparison_plots/nonuniform_plot_comparison_map_MMI_$realisation/c000.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/MMI.png
      else
        cp /home/nesi00213/groundfailure/scripts/Data/Placeholder.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/MMI.png
      fi
    
    
      if [ -f $run_dir/$run_name/GM/Validation/$realisation/Data/nonuniform_im_plot_map_$realisation'.xyz' ]; then
        # PGA
        name_of_plot=`python /home/nesi00213/groundfailure/scripts/find_plot.py -r $realisation -n 'PGA' -v $run -f $run_name`
        if [ -f /home/nesi00213/RunFolder/Cybershake/$run/Runs/$run_name/GM/Validation/$realisation/Data/nonuniform_im_plot_map_$realisation/$name_of_plot ]; then
          cp /home/nesi00213/RunFolder/Cybershake/$run/Runs/$run_name/GM/Validation/$realisation/Data/nonuniform_im_plot_map_$realisation/$name_of_plot $out_dir/website_data/$run/$run_name/$realisation/PNGs/PGA.png
        else
          cp /home/nesi00213/groundfailure/scripts/Data/Placeholder.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/PGA.png
        fi
        
        # PGV
        name_of_plot=`python /home/nesi00213/groundfailure/scripts/find_plot.py -r $realisation -n 'PGV' -v $run -f $run_name`
        if [ -f /home/nesi00213/RunFolder/Cybershake/$run/Runs/$run_name/GM/Validation/$realisation/Data/nonuniform_im_plot_map_$realisation/$name_of_plot ]; then
          cp /home/nesi00213/RunFolder/Cybershake/$run/Runs/$run_name/GM/Validation/$realisation/Data/nonuniform_im_plot_map_$realisation/$name_of_plot $out_dir/website_data/$run/$run_name/$realisation/PNGs/PGV.png
        else
          cp /home/nesi00213/groundfailure/scripts/Data/Placeholder.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/PGV.png
        fi
      else
        cp /home/nesi00213/groundfailure/scripts/Data/Placeholder.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/PGA.png
        cp /home/nesi00213/groundfailure/scripts/Data/Placeholder.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/PGV.png
      fi

      # Liquefaction Population CCDF - currently unverified
      if [ -f /home/nesi00213/RunFolder/Cybershake/$run/Runs/$run_name/Impact/Liquefaction/$realisation/CCDF/*Population*general_probability_nz-specific-vs30.png ]; then
        cp /home/nesi00213/RunFolder/Cybershake/$run/Runs/$run_name/Impact/Liquefaction/$realisation/CCDF/*Population*general_probability_nz-specific-vs30.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/LiquefactionPopulationCCDF.png
      else
        cp /home/nesi00213/groundfailure/scripts/Data/Placeholder.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/LiquefactionPopulationCCDF.png
      fi
      
      # Landslide Population CCDF - currently unverified
      if [ -f /home/nesi00213/RunFolder/Cybershake/$run/Runs/$run_name/Impact/Landslide/$realisation/CCDF/*Population*.png ]; then
        cp /home/nesi00213/RunFolder/Cybershake/$run/Runs/$run_name/Impact/Landslide/$realisation/CCDF/*Population*.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/LandslidePopulationCCDF.png
      else
        cp /home/nesi00213/groundfailure/scripts/Data/Placeholder.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/LandslidePopulationCCDF.png
      fi
      
      # Wave Video
      if [ -f /home/nesi00213/RunFolder/Cybershake/$run/Runs/$run_name/Impact/GM/*.m4v ]; then
        cp /home/nesi00213/RunFolder/Cybershake/$run/Runs/$run_name/Impact/Liquefaction/$realisation/*c-vs30_probability_general.png $out_dir/website_data/$run/$run_name/$realisation/videos/Wave_Propagation.m4v
      else
        cp /home/nesi00213/groundfailure/scripts/Data/Placeholder.png $out_dir/website_data/$run/$run_name/$realisation/videos/Wave_Propagation.m4v
      fi
      
      # Liquefaction Dwelling CCDF - currently unverified
      if [ -f /home/nesi00213/RunFolder/Cybershake/$run/Runs/$run_name/Impact/Liquefaction/$realisation/CCDF/*Dwellings*general_probability_nz-specific-vs30.png ]; then
        cp /home/nesi00213/RunFolder/Cybershake/$run/Runs/$run_name/Impact/Liquefaction/$realisation/CCDF/*Dwellings*general_probability_nz-specific-vs30.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/LiquefactionDwellingsCCDF.png
      else
        cp /home/nesi00213/groundfailure/scripts/Data/Placeholder.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/LiquefactionDwellingsCCDF.png
      fi
      
      # Landslide Dwelling CCDF - currently unverified
      if [ -f /home/nesi00213/RunFolder/Cybershake/$run/Runs/$run_name/Impact/Landslide/$realisation/CCDF/*Dwellings*.png ]; then
        cp /home/nesi00213/RunFolder/Cybershake/$run/Runs/$run_name/Impact/Landslide/$realisation/CCDF/*Dwellings*.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/LandslideDwellingsCCDF.png
      else
        cp /home/nesi00213/groundfailure/scripts/Data/Placeholder.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/LandslideDwellingsCCDF.png
      fi

      # Liquefaction map
      if [ -f /home/nesi00213/RunFolder/Cybershake/$run/Runs/$run_name/Impact/Liquefaction/$realisation/*c-vs30_probability_general.png ]; then
        cp /home/nesi00213/RunFolder/Cybershake/$run/Runs/$run_name/Impact/Liquefaction/$realisation/*c-vs30_probability_general.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/LiquefactionProbability.png
      else
        cp /home/nesi00213/groundfailure/scripts/Data/Placeholder.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/LiquefactionProbability.png
      fi
      
      # Landslide map
      if [ -f /home/nesi00213/RunFolder/Cybershake/$run/Runs/$run_name/Impact/Landslide/$realisation/*probability_.png ]; then
        cp /home/nesi00213/RunFolder/Cybershake/$run/Runs/$run_name/Impact/Landslide/$realisation/*probability_.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/LandslideProbability.png
      else
        cp /home/nesi00213/groundfailure/scripts/Data/Placeholder.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/LandslideProbability.png
      fi
      
      # Liquefaction Area CCDF
      if [ -f /home/nesi00213/RunFolder/Cybershake/$run/Runs/$run_name/Impact/Liquefaction/$realisation/CCDF/*Area*general_probability_nz-specific-vs30.png ]; then
        cp /home/nesi00213/RunFolder/Cybershake/$run/Runs/$run_name/Impact/Liquefaction/$realisation/CCDF/*Area*general_probability_nz-specific-vs30.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/LiquefactionAreaCCDF.png
      else
        cp /home/nesi00213/groundfailure/scripts/Data/Placeholder.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/LiquefactionAreaCCDF.png
      fi
      
      # Landslide Area CCDF
      if [ -f /home/nesi00213/RunFolder/Cybershake/$run/Runs/$run_name/Impact/Landslide/$realisation/CCDF/*Area*.png ]; then
        cp /home/nesi00213/RunFolder/Cybershake/$run/Runs/$run_name/Impact/Landslide/$realisation/CCDF/*Area*.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/LandslideAreaCCDF.png
      else
        cp /home/nesi00213/groundfailure/scripts/Data/Placeholder.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/LandslideAreaCCDF.png
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
zip -r website_data . >/dev/null