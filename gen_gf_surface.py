#!/usr/bin/env python2
"""
Takes a h5 output file from USGS's groundfailure code and converts into
a format that can be plotted from plot_stations.py

Usage gen_gf_surface.py "file.h5"

writes "file.xyz" containing the data to be plotted

@date 5 Jul 2017
@author Jason Motha
@contact jason.motha@canterbury.ac.nz
"""

import sys
import os
import h5py
import math
import argparse

## Parse Arguements

parser = argparse.ArgumentParser(description='Convert a USGS H5 file to xyz for plotting with "plot_stations.py"')

parser.add_argument('filename', help='Filename of h5 file to convert')

parser.add_argument('-m', '--model',  default=2, choices=[1,2], type=int,
                    help='Selects which model has been used: 1- coastal 2- general (default) (determines text on figures)')
parser.add_argument('-l', '--limit', default=float('-inf'), type=float,
                    help='Specifies a threshold value - useful for removing unnecessary fill')
parser.add_argument('-s', '--susceptibility', default=False, action="store_true", help='Changes the plot labels to indicate susceptibility ')
parser.add_argument('-t', '--title', help='Title for the top of the graph. Defaults to a trimmed run_name')
parser.add_argument('-o', '--output', default=None, help='sets the name of the output file') 

args = parser.parse_args()

fname = args.filename
threshold = args.limit
susceptibility = args.susceptibility
model = args.model
plot_title = args.title
fout_name = args.output

## Read H5 file to be converted

f = h5py.File(fname, 'r')

lat = list(f['x'])
lon = list(f['y'])
values = list(f['model'])


basename = fname.split('.')[0]

## Write output file

if fout_name is None:
    fout_name = basename + '.xyz'
with open(fout_name, 'w') as fout:

    if plot_title is not None:
        plot_title += '\n'
    else:
        plot_title = basename[0:20] + '\n'
    fout.write(plot_title)

    #hot:invert,t-30 1k:g-nearneighbor
    #/home/nesi00213/qcore/plot/cpt/liquifaction-nolabel.cpt:fixed,categorical,t-40 1k:g-nearneighbor
    fout.write('Liquefaction ')
    if susceptibility:
        fout.write("Susceptibility \n<REPO>/liquefaction-nolabel.cpt:topo-grey1,fixed,categorical,t-30 1k:g-nearneighbor,landmask\n\n")
    else:
        fout.write("Probability \nhot:topo-grey1,invert,t-30 1k:g-nearneighbor,landmask\n0 1 0.02 0.1\n")

    fout.write("1 white\n")

    if model == 1:
        fout.write("Coastal Model\n")
    else:
        fout.write("General Model\n")

    len_lon = len(lon)
    vmax = -float('inf')
    vmin = float('inf')

    if threshold > float('-inf'):
        print "Filtering values below %f" % threshold
        

    for i in xrange(len_lon):
        for j in xrange(len(lat)):
            val = values[i][j]
            if not math.isnan(val) and not math.isinf(val):
                if val > threshold:
                    fout.write("%f %f %f\n" % (lat[j], lon[len_lon - i - 1], val))
                    vmax = max(vmax, val)
                    vmin = min(vmin, val)

    print "max value: %f \t min value: %f" % (vmax, vmin)


                        
