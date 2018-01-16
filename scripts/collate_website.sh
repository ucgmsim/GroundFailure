#!/bin/bash

out_dir=${1:-'.'}
if [[ $out_dir == '.' ]]; then
  out_dir=`pwd`
fi

#list_runs_v17p8=`cat /home/nesi00213/RunFolder/Cybershake/v17p8/temp/list_runs_v17p8`
#list_runs_v17p9=`cat /home/nesi00213/RunFolder/Cybershake/v17p9/temp/list_runs_v17p9`
#run_dir_8='/home/nesi00213/RunFolder/Cybershake/v17p8/Runs'
#run_dir_9='/home/nesi00213/RunFolder/Cybershake/v17p9/Runs'

mkdir $out_dir/website_data/
#mkdir $out_dir/website_data/v17p8
#mkdir $out_dir/website_data/v17p9

cp /home/lukelongworth/Data/NZ_FLTmodel_2010.txt $out_dir # DISTURBINGLY HARD-CODED

list1=(v17p8 v17p9)

for run in $list1
do
  list='list_runs_'$run
  mkdir $out_dir/website_data/$run
  
  for run_name in `cat /home/nesi00213/RunFolder/Cybershake/v17p8/temp/$list`
  do
    run_dir='/home/nesi00213/RunFolder/Cybershake/'$run'/Runs'
    mkdir $out_dir/website_data/$run/$run_name
    cd $run_dir/$run_name/GM/Validation
    ls -1 -d *HYP* > $out_dir/website_data/$run/$run_name/realisation_list.txt
    for realisation in `cat $out_dir/website_data/$run/$run_name/realisation_list.txt`
    do
      # echo $realisation
      mkdir $out_dir/website_data/$run/$run_name/$realisation/
      mkdir $out_dir/website_data/$run/$run_name/$realisation/PNGs/
      # cp MMI map
      # cp PGA map
      # cp PGV map
      cp /home/nesi00213/RunFolder/Cybershake/$run/Runs/$run_name/Impact/Liquefaction/$realisation/*c-vs30_probability_general.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/LiquefactionProbability.png
      cp /home/nesi00213/RunFolder/Cybershake/$run/Runs/$run_name/Impact/Landslide/$realisation/*probability_.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/LandslideProbability.png# cp ls prob map
      cp /home/nesi00213/RunFolder/Cybershake/$run/Runs/$run_name/Impact/Liquefaction/$realisation/CCDF/*general_probability_nz-specific-vs30.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/LiquefactionCCDF.png
      cp /home/nesi00213/RunFolder/Cybershake/$run/Runs/$run_name/Impact/Landslide/$realisation/CCDF/*.png $out_dir/website_data/$run/$run_name/$realisation/PNGs/LandslideCCDF.png
    done
  done
  cd $out_dir
  python /home/nesi00213/groundfailure/scripts/gen_Fault_Info.py $run $out_dir
done

rm $out_dir/NZ_FLTmodel_2010.txt

