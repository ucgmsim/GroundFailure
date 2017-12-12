# This code finds the corners of a surface for a given realisation
# It is designed to work with the cybershake_run_liqls.sh in /home/lukelongworth
# Inputs: The directory containing the runs for a given dataset (eg. v17p8)
#         The name of the fault
#         The name of the realisation
# These inputs are equivalent to $run_dir, $run_name and $realisation which are variables in the aforementioned shell
# Outputs: A filepath to the relevant file
import argparse

#Initialisation
parser = argparse.ArgumentParser()
parser.add_argument("rd")
parser.add_argument("rn")
parser.add_argument("re")

args = parser.parse_args()

run_dir = args.rd
run_name = args.rn
realisation = args.re

# Piece together the relevant bits to create a MEGASTRING to the filepath
print run_dir+"/"+run_name+"/GM/Sim/Data/"+run_name+"/"+realisation+"/corners.txt"