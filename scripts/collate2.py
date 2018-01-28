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
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-p','--probabilities')
args = parser.parse_args()

# Loading probabilities into the correct format
probabilities = args.probabilities # eg. probabilities = 0.8,0.5,0.1
probabilities = probabilities.split(',') # eg. probabilities = ['0.8','0.5','0.1']

i = 0
for prob in probabilities:
    probabilities[i] = float(prob)
    i += 1
# Now the list entries are floats, not strings

n_probs = len(probabilities)

# Load the relevant files 
files = glob.glob('*y.txt.xyz')
# print files
fs = []

files.sort(reverse=True)

for file in files:
  #print(file)
  fs.append(open(file))
  
for file in fs:
  file.readline()
  file.readline()
  file.readline()
  file.readline()
  file.readline()
  file.readline()
  file.readline()

# probabilities = [float(f.split('_')[0].replace('p', '.')) for f in files]

#sys.stderr.write(','.join(probabilities) + '\n')

n_lines = 0
discrepancy_count = 0
prev_lat = 0
prev_lon = 0

while 1:
  probs = []
  prob_sum = 0
  i = 0
  n_lines += 1
  
  for f in fs:
    a = f.readline()
    lon, lat, liq_prob = a.split()
    
    liq_prob = float(liq_prob)
    i1 = min(i, n_probs-2)
    i2 = min(i+1, n_probs - 1)
    delta_haz = probabilities[i1] - probabilities[i2]
    prob_sum += delta_haz * liq_prob 
    probs.append(liq_prob)
    #print delta_haz, liq_prob
    
    i += 1
    #print lon, lat, ', '.join(probs)
    if prev_lat != lat or prev_lon != lon:
      discrepancy_count += 1
    prev_lat = lat
    prev_lon = lon
  print lon, lat, prob_sum, ' '.join(map(str, probs))
  sys.stderr.write('lines: %d discrepancies: %d\n' % (n_lines, discrepancy_count-n_lines))