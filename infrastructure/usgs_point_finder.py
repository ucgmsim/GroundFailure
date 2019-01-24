#!/usr/bin/env python

"""
For each line in a given file with longitude and latitude data append the name of the nearest ground failure as given
by the input hdf5 file
"""

import argparse
#import time as time
from mapio.multihaz import MultiHazardGrid
from mapio.dataset import DataSetException
import pandas as pd


def ground_failure_finder(ls_file, csv_file, output_file):
    # Load data
    grid = MultiHazardGrid.load(ls_file)
    keys = list(grid.getLayerNames())
    data = grid.getData()[keys[0]]
    
    csv_data = pd.read_csv(csv_file, index_col=0, encoding="ISO-8859-1")

    csv_data = csv_data.assign(GROUNDFAILURE="")
    #time1 = time.time()
    for i in range(len(csv_data)):
        lat, lon = csv_data.iloc[i][["LAT", "LONG"]]
        try:
            # Converted to string to catch 'nan' passed from hdf5
            csv_data.at[i, "GROUNDFAILURE"] = str(data.getValue(lat, lon))
        except DataSetException as e:
            csv_data.at[i, "GROUNDFAILURE"] = "nan"
    
    #interp_time = time.time() - time1
    #print("Interpolation time: %s sec" % interp_time)
    csv_data.to_csv(output_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('hdf5file', help='ground failure hdf file.')
    parser.add_argument('csvfile', help='location csv file.')
    parser.add_argument('outfile', help='output csv file name.')
    args = parser.parse_args()
    ground_failure_finder(args.hdf5file, args.csvfile, args.outfile)
