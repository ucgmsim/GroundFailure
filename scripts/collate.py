'''
This script is used within the shell script /home/nes100213/groundfailure/scripts/hazard_prob_plot.sh
It takes the information generated and outputs new relevant information
The shell script pipes the output into a new file

The input is a singular input; a list of probabilities.
These probabilities are an input into the parent shell script in the correct format
They are input as a string; eg 0.8,0.5,0.1,0.05,0.01

Usage and example:
python /path/to/script/collate2.py -p 'Probabilities'
python $source_folder/HazMapData/xyz/collate2.py -p $probabilities

Modified version of collate.py by Jason Motha
Created by Luke Longworth | luke.longworth.nz@gmail.com
'''
# Initialising
import glob
import sys
import os
import argparse
import itertools

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--inputdir', default=os.getcwd(), help='Directory that contains the probability xyz files')
parser.add_argument('-o', '--outputfile', default=os.getcwd(), help='The path to the output-file to be created')

args = parser.parse_args()

input_filenames = os.path.join(args.inputdir, '*y.txt.xyz')

# Load the relevant files 
files = glob.glob(input_filenames)
fs = []

out_f = open(args.outputfile, 'w')

#sorts the files with the largest probability first
files.sort(reverse=True)

#extracts probabilities from filename
probabilities = [float(os.path.basename(f).split('_')[1].replace('p', '.')) for f in files] #extracts the probability from the filename as a float
n_probs = len(probabilities)

fs = [open(f) for f in files]

#skips the headers for all of the files
for f in fs:
  f.readline()
  f.readline()
  f.readline()
  f.readline()
  f.readline()
  f.readline()
  f.readline()

n_lines = 0
discrepancy_count = 0
prev_lat = 0
prev_lon = 0

for lines in itertools.izip(*fs):
  probs = []
  prob_sum = 0
  i = 0
  n_lines += 1
  
  for line in lines:
    lon, lat, liq_prob = line.split()
    
    liq_prob = float(liq_prob)
    # find indexes of probabilities from file order
    i1 = min(i, n_probs-2)
    i2 = min(i+1, n_probs - 1)
    delta_haz = probabilities[i1] - probabilities[i2]
    
    prob_sum += delta_haz * liq_prob 
    probs.append(liq_prob)
    #print delta_haz, liq_prob
    
    i += 1
    if prev_lat != lat or prev_lon != lon:
      discrepancy_count += 1
    prev_lat = lat
    prev_lon = lon
  out_f.write('%s %s %s %s\n' % (lon, lat, prob_sum, ' '.join(map(str, probs))))
  # sys.stderr.write('lines: %d discrepancies: %d\n' % (n_lines, discrepancy_count-n_lines))
    
if discrepancy_count - n_lines > 0:
    sys.stderr.write("There has been an error in the collation; please check files are of same length")


