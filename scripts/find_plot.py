'''
This script was written for use in collate_website.sh and is used to find which of the many nonuniform im plots are the relevant ones
It was written because roughly 20 plots are produced for each realisation and they are not produced in the same order for each realisation. They all have helpful names; c000, c001, c002, c003, ..., c020, etc.
It outputs the name of the file that contains the relevant plot

Inputs: -r name_of_the_realisation, eg AlpineF2K_HYP01-03_S1254
        -n name_of_the_plot, eg PGV, PGA, pSa(0.1), etc. THIS MUST CONTAIN NO SPACES
        -v cybershake_run_code, eg v17p8
        -f fault_name, eg. AlpineF2K
All inputs are compulsory for the function to work, collate_website.sh has all of these except -n as variables anyway.

Output: A string similar to 'c021.png' that will tell you which plot you want.

Examples: python /home/nesi00213/groundfailure/scripts/find_plot.py -r Albury_HYP01-01_S1244 -n 'pSa(0.1)' -v v17p9 -f Albury
          python /home/nesi00213/groundfailure/scripts/find_plot.py -r $realisation -n 'PGA' -v $run -f $run_name
          
Written by Luke Longworth on 07/02/2018
Contact at luke.longworth.nz@gmail.com
'''

# Initialisation and argument interpretation
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('-r', '--realisation', help='Name of the realisation, eg AlpineF2K_HYP01-03_S1254')
parser.add_argument('-n', '--name', help='Name of the plot you are looking for, PGV or PGA')
parser.add_argument('-v', '--run', help='The run in question, eg v17p8 or v17p9')
parser.add_argument('-f', '--fault', help='The name of the fault')

args = parser.parse_args()

realisation = args.realisation
name = args.name
run = args.run
fault = args.fault

# Open the relevant file
f = open(os.path.join(os.path.sep,'home','nesi00213','RunFolder','Cybershake',run,'Runs',fault,'GM','Validation',realisation,'Data','nonuniform_im_plot_map_'+realisation+'.xyz'),'r')

# Convert the file into a list of strings
info = f.readlines()[0:6]
info = info[-1]
info = info.replace(' ', '')
info = info.replace('\n','')
info = info.split(',')
number_plots = len(info)

# Find the index number in the string that produces the same string as the input -n
# For example, if we are looking for PGV and the string that matches 'PGV' is indexed at 18, i will return 18.
i = str(info.index(name))

# Format this into the correct format
if len(i) == 1:
    i = 'c00'+i+'.png'
elif len(i) == 2:
    i = 'c0'+i+'.png'

# Print the output. In collate_website.sh this is piped into a variable.
print i