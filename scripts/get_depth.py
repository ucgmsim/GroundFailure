# This code finds the depth of a given realisation
# It is designed to work with the cybershake_run_liqls.sh in /home/lukelongworth/USER
# Inputs: The filepath to the Sim/Data of a particular realisation
#         e.g. /home/nesi00213/Runfolder/Cybershake/v17p8/Runs/AlpineF2K/GM/Validation/AlpineF2K_HYP01-03_S1254
# Outputs: A float representing the depth of the rupture

#import ConfigParser
# import os
import argparse

#Initialisation
#config = ConfigParser.RawConfigParser()
parser = argparse.ArgumentParser()
parser.add_argument("rp")

args = parser.parse_args()
realisation_path = args.rp

#Get the data
#os.chdir(realisation_path) #Go to relevant directory
#config.read("pp_config.cfg") #Open the relevant config file
#print config.get("plotGMPE", "Ztor") #Grab and print the depth

depth = open(realisation_path+"/hypo_depth.txt")
print depth.readline()