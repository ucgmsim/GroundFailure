#!/bin/bash

#This is a one-time-use code (that is easily editable) to produce a bunch of similar grid.xml files for comparison. This was specifically designed to take different grid resolutions and compare them.

cd /home/nesi00213/dev/post-processing/scripts/

# AlpineF2K_HYP01-03_S1244
python export_lonlat_pgv2csv.py /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/AlpineF2K/GM/Validation/AlpineF2K_HYP01-03_S1244/Data/database.db /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/AlpineF2K/GM/Sim/Data/AlpineF2K/AlpineF2K_HYP01-03_S1244/

mag=`python /home/lukelongworth/get_mag.py /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/AlpineF2K/GM/Validation/AlpineF2K_HYP01-03_S1244/`
depth=`python /home/lukelongworth/get_depth.py /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/AlpineF2K/GM/Validation/AlpineF2K_HYP01-03_S1244/`
corners=`python /home/lukelongworth/get_corners.py /home/nesi00213/RunFolder/Cybershake/v17p8/Runs AlpineF2K AlpineF2K_HYP01-03_S1244`

python /home/nesi00213/groundfailure/haz_analysis/grd2grid.py /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/AlpineF2K/GM/Sim/Data/AlpineF2K/AlpineF2K_HYP01-03_S1244/lonlatpgv_database.csv AlpineF2K_HYP01-03_S1244 /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/AlpineF2K/GM/Sim/Data/AlpineF2K/AlpineF2K_HYP01-03_S1244/ -m $mag -d $depth -c $corners --dx 2k

cp /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/AlpineF2K/GM/Sim/Data/AlpineF2K/AlpineF2K_HYP01-03_S1244/grid.xml /home/lukelongworth/grid_A_2k.xml

python /home/nesi00213/groundfailure/haz_analysis/grd2grid.py /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/AlpineF2K/GM/Sim/Data/AlpineF2K/AlpineF2K_HYP01-03_S1244/lonlatpgv_database.csv AlpineF2K_HYP01-03_S1244 /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/AlpineF2K/GM/Sim/Data/AlpineF2K/AlpineF2K_HYP01-03_S1244/ -m $mag -d $depth -c $corners --dx 4k

cp /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/AlpineF2K/GM/Sim/Data/AlpineF2K/AlpineF2K_HYP01-03_S1244/grid.xml /home/lukelongworth/grid_A_4k.xml

python /home/nesi00213/groundfailure/haz_analysis/grd2grid.py /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/AlpineF2K/GM/Sim/Data/AlpineF2K/AlpineF2K_HYP01-03_S1244/lonlatpgv_database.csv AlpineF2K_HYP01-03_S1244 /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/AlpineF2K/GM/Sim/Data/AlpineF2K/AlpineF2K_HYP01-03_S1244/ -m $mag -d $depth -c $corners --dx 8k

cp /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/AlpineF2K/GM/Sim/Data/AlpineF2K/AlpineF2K_HYP01-03_S1244/grid.xml /home/lukelongworth/grid_A_8k.xml

# HopeConwayOS_HYP03-03_S1294
python export_lonlat_pgv2csv.py /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/HopeConwayOS/GM/Validation/HopeConwayOS_HYP03-03_S1294/Data/database.db /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/HopeConwayOS/GM/Sim/Data/HopeConwayOS/HopeConwayOS_HYP03-03_S1294/

mag=`python /home/lukelongworth/get_mag.py /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/HopeConwayOS/GM/Validation/HopeConwayOS_HYP03-03_S1294/`
depth=`python /home/lukelongworth/get_depth.py /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/HopeConwayOS/GM/Validation/HopeConwayOS_HYP03-03_S1294/`
corners=`python /home/lukelongworth/get_corners.py /home/nesi00213/RunFolder/Cybershake/v17p8/Runs HopeConwayOS HopeConwayOS_HYP03-03_S1294`

python /home/nesi00213/groundfailure/haz_analysis/grd2grid.py /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/HopeConwayOS/GM/Sim/Data/HopeConwayOS/HopeConwayOS_HYP03-03_S1294/lonlatpgv_database.csv HopeConwayOS_HYP03-03_S1294 /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/HopeConwayOS/GM/Sim/Data/HopeConwayOS/HopeConwayOS_HYP03-03_S1294/ -m $mag -d $depth -c $corners --dx 2k

cp /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/HopeConwayOS/GM/Sim/Data/HopeConwayOS/HopeConwayOS_HYP03-03_S1294/grid.xml /home/lukelongworth/grid_H_2k.xml

python /home/nesi00213/groundfailure/haz_analysis/grd2grid.py /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/HopeConwayOS/GM/Sim/Data/HopeConwayOS/HopeConwayOS_HYP03-03_S1294/lonlatpgv_database.csv HopeConwayOS_HYP03-03_S1294 /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/HopeConwayOS/GM/Sim/Data/HopeConwayOS/HopeConwayOS_HYP03-03_S1294/ -m $mag -d $depth -c $corners --dx 4k

cp /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/HopeConwayOS/GM/Sim/Data/HopeConwayOS/HopeConwayOS_HYP03-03_S1294/grid.xml /home/lukelongworth/grid_H_4k.xml

python /home/nesi00213/groundfailure/haz_analysis/grd2grid.py /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/HopeConwayOS/GM/Sim/Data/HopeConwayOS/HopeConwayOS_HYP03-03_S1294/lonlatpgv_database.csv HopeConwayOS_HYP03-03_S1294 /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/HopeConwayOS/GM/Sim/Data/HopeConwayOS/HopeConwayOS_HYP03-03_S1294/ -m $mag -d $depth -c $corners --dx 8k

cp /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/HopeConwayOS/GM/Sim/Data/HopeConwayOS/HopeConwayOS_HYP03-03_S1294/grid.xml /home/lukelongworth/grid_H_8k.xml

# Kelly_HYP03-03_S1294

python export_lonlat_pgv2csv.py /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/Kelly/GM/Validation/Kelly_HYP03-03_S1294/Data/database.db /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/Kelly/GM/Sim/Data/Kelly/Kelly_HYP03-03_S1294/

mag=`python /home/lukelongworth/get_mag.py /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/Kelly/GM/Validation/Kelly_HYP03-03_S1294/`
depth=`python /home/lukelongworth/get_depth.py /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/Kelly/GM/Validation/Kelly_HYP03-03_S1294/`
corners=`python /home/lukelongworth/get_corners.py /home/nesi00213/RunFolder/Cybershake/v17p8/Runs Kelly Kelly_HYP03-03_S1294`

python /home/nesi00213/groundfailure/haz_analysis/grd2grid.py /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/Kelly/GM/Sim/Data/Kelly/Kelly_HYP03-03_S1294/lonlatpgv_database.csv Kelly_HYP03-03_S1294 /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/Kelly/GM/Sim/Data/Kelly/Kelly_HYP03-03_S1294/ -m $mag -d $depth -c $corners --dx 2k

cp /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/Kelly/GM/Sim/Data/Kelly/Kelly_HYP03-03_S1294/grid.xml /home/lukelongworth/grid_K_2k.xml

python /home/nesi00213/groundfailure/haz_analysis/grd2grid.py /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/Kelly/GM/Sim/Data/Kelly/Kelly_HYP03-03_S1294/lonlatpgv_database.csv Kelly_HYP03-03_S1294 /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/Kelly/GM/Sim/Data/Kelly/Kelly_HYP03-03_S1294/ -m $mag -d $depth -c $corners --dx 4k

cp /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/Kelly/GM/Sim/Data/Kelly/Kelly_HYP03-03_S1294/grid.xml /home/lukelongworth/grid_K_4k.xml

python /home/nesi00213/groundfailure/haz_analysis/grd2grid.py /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/Kelly/GM/Sim/Data/Kelly/Kelly_HYP03-03_S1294/lonlatpgv_database.csv Kelly_HYP03-03_S1294 /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/Kelly/GM/Sim/Data/Kelly/Kelly_HYP03-03_S1294/ -m $mag -d $depth -c $corners --dx 8k

cp /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/Kelly/GM/Sim/Data/Kelly/Kelly_HYP03-03_S1294/grid.xml /home/lukelongworth/grid_K_8k.xml
