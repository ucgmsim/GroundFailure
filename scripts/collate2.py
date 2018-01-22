import glob
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-p','--probabilities')
args = parser.parse_args()

probabilities = args.probabilities
probabilities = probabilities.split(',')

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
i = 0
for prob in probabilities:
    probabilities[i] = float(prob)
    i += 1

n_probs = len(probabilities)

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