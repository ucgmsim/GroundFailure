'''
This code finds the depth of a given realisation
It is designed to work with the cybershake_run_liqls.sh in /home/nesi00213/groundfailure/scripts/

Inputs: The filepath to the Sim/Data of a particular realisation
        e.g. /home/nesi00213/Runfolder/Cybershake/v17p8/Runs/AlpineF2K/GM/Validation/AlpineF2K_HYP01-03_S1254
Outputs: A float representing the depth of the rupture

Usage and example
python /path/to/script/get_depth.py /path/to/realisation/validation/folder
python /home/nesi00213/groundfailure/scripts/get_depth.py $realisation_path
python /home/nesi00213/groundfailure/scripts/get_depth.py /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/AlpineF2K/GM/Validation/AlpineF2K_HYP01-03_S1254/

Written by Luke Longworth | luke.longworth.nz@gmail.com
'''
import argparse

# Initialisation
parser = argparse.ArgumentParser()
parser.add_argument("rp")

args = parser.parse_args()
realisation_path = args.rp

# Open the file and print the contents
def depth(realisation_path):
  depth = open(realisation_path+"/hypo_depth.txt")
  print depth.readline()