"""
Author-email: jason.motha@canterbury.ac.nz
This file converts a Hazard file output from either empirical and cybershake into a corresponding output file for a specified probability and year

"""
import numpy as np
import sys
import argparse
import os

print "Why won't this print???"

def get_lat(header):
    lat_end_pos = header.index('_')
    return header[3:lat_end_pos].replace('p', '.')


def get_lon(header):
    lon_index = header.index('Lon') + len('Lon')
    lon_end_pos = header[lon_index:].index('_') + lon_index
    return header[lon_index:lon_end_pos].replace('p', '.')


def find_cart_grid(s1, s2):
    check1 = round(float(s1), 4)
    check2 = round(float(s2), 4)
    return check1 == check2

parser = argparse.ArgumentParser()
parser.add_argument('inputfile', type=str, help='The file on which the script is run')
parser.add_argument('-i', '--inputdir', default=os.getcwd(), help='Where to find the inputfile')
parser.add_argument('-y', '--years', default=50.0, help='The number of years over which the analysis will be calculated')
parser.add_argument('-p', '--probabilities', help='The probability bins into which the data will be sorted')
parser.add_argument('-o', '--outputdir', default=os.getcwd(), help='The directory to put the new .txt files into')

args = parser.parse_args()

inputfile = args.inputfile
input_dir = args.inputdir
output_dir = args.outputdir
years = float(args.years)

if args.probabilities == None:
  print("The probabilities value has not been given")
  probs = [0.8, 0.5, 0.25, 0.1, 0.08, 0.06, 0.04, 0.02, 0.01, 0.005]
else:
  print("The probabilities value has been given")
  probs = args.probabilities
  probs = probs.split(',')
  ii = 0
  while ii < len(probs):
    print(ii)
    probs[ii] = float(probs[ii])
    ii += 1
    

print(inputfile)
print(input_dir)
print(output_dir)
print(type(years))
print(years)
print(type(probs[1]))
print(probs)

for sProb in probs:
    print("The specific probability is %.4f" % (sProb))
    specificRate = (-np.log(1-sProb)) / years
    print("The specific rate is %.4f" % (specificRate))
    prob = specificRate
    values = []

    with open(inputfile) as f:
        fp = iter(f)
        for line in fp:
            header = line
            while len(header.strip()) <= 0:
                try:
                    header = next(fp)
                except StopIteration:
                    break
            if len(header.strip()) <= 0:
                break

            lat = get_lat(header)
            lon = get_lon(header)

            pgv_line = next(fp)
            pgv_vals = np.array(map(np.float, pgv_line.split('\t')[:-1]))

            prob_line = next(fp)
            prob_vals = np.array(map(np.float, prob_line.split('\t')[:-1]))

            closest_index = np.argmin(np.abs(prob_vals - prob))

            closest_prob = prob_vals[closest_index]
            closest_pgv = pgv_vals[closest_index]

            if (closest_index == 0 or closest_prob <= prob) and closest_index < len(prob_vals) - 1:
                paired_index = closest_index + 1
            else:
                paired_index = closest_index - 1


            paired_prob = prob_vals[paired_index]
            paired_pgv = pgv_vals[paired_index]

            slope = np.abs((paired_prob - closest_prob) / (paired_pgv - closest_pgv))

            pgv = closest_pgv + (closest_prob - prob) * slope

            out = (lat, lon, pgv, prob, slope)
            values.append(out)

    # values.sort(key=lambda tup: (tup[0], tup[1]))
    values.sort()

    count = 0
    ncount = 0

    fname =  output_dir+'/'+'pgv_%.4f_%.0fy.txt' % (sProb, years)
    
    with open(fname, 'w+') as fw:
        with open('non_uniform_whole_nz-hh400.ll') as f:
            for value in values:
                lat, lon, pgv, prob, slope = value
                f.seek(0)
                for line in f:
                    grid_lon, grid_lat, site_name, grid_x, grid_y = line.split()
                    if find_cart_grid(lat, grid_lat):
                        if find_cart_grid(lon, grid_lon):
                            count += 1
                            fw.write("%s %s %f\n" % (lon, lat, pgv))
                            #print grid_lat, grid_lon, lat, lon, site_name, grid_x, grid_y, pgv, prob, slope

                sys.stderr.write("%d %d\n" % (count, len(values)))

