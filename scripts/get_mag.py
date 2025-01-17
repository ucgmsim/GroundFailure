'''
This code finds the magnitude of a given realisation
It is designed to work with the cybershake_run_liqls.sh in /home/nesi00213/groundfailure/scripts/

Inputs: The filepath to a particular realisation
        e.g. /home/nesi00213/Runfolder/Cybershake/v17p8/Runs/AlpineF2K/GM/Validation/AlpineF2K_HYP01-03_S1254
Outputs: A float representing the magnitude

Usage and examples
python /path/to/script/get_mag.py /path/to/realisation/directory/
python /home/nesi00213/groundfailure/scripts/get_mag.py $realisation_path
python /home/nesi00213/groundfailure/scripts/get_mag.py /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/AlpineF2K/GM/Validation/AlpineF2K_HYP01-03_S1254/

Written by Luke Longworth | luke.longworth.nz@gmail.com
'''
import ConfigParser
import os
import argparse

#Initialisation
config = ConfigParser.RawConfigParser()
parser = argparse.ArgumentParser()
parser.add_argument("rp")

args = parser.parse_args()
realisation_path = args.rp

# Grab the data
os.chdir(realisation_path) #Go to the relevant directory
config.read("pp_config.cfg") #Open the relevant config file
print config.get("plotGMPE", "Mw") #Get and print the magnitude
