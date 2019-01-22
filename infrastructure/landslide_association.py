#!/usr/bin/env python

import argparse
import time as time
import numpy as np
from mapio.multihaz import MultiHazardGrid
from mapio.dataset import DataSetException
import pandas as pd

def main(args):
    ls_file = args.hdf5file
    csv_file = args.csvfile
    #n_sample = int(args.n)
    # Load data
    grid = MultiHazardGrid.load(ls_file)
    keys = list(grid.getLayerNames())
    data = grid.getData()[keys[0]]
    #geo_dict = data.getGeoDict()
    
    csv_data = pd.read_csv(csv_file)
    #x_samples = csv_data["LONG"].tolist()
    #y_samples = csv_data["LAT"].tolist()
    #imin = 0
    #imax = len(csv_data)

    # Random sample locations
    #x_index_samples = np.random.randint(imin, imax, n_sample)
    #y_index_samples = np.random.randint(imin, imax, n_sample)
    #samples = np.zeros(len(csv_data))

    # Do the interpolation

    csv_data = csv_data.assign(LANDSLIDE="")
    time1 = time.time()
    for i in range(len(csv_data)):
        lat, lon = csv_data.iloc[i][["LAT","LONG"]]
        try:
            csv_data.at[i, "LANDSLIDE"] = data.getValue(lat, lon)
        except DataSetException as e:
            csv_data.at[i, "LANDSLIDE"] = "NaN"
    
    interp_time = time.time() - time1
    print("Interpolation time: %s sec" % interp_time)
    csv_data.to_csv(args.outfile)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('hdf5file', help='groundfailure hdf file.')
    parser.add_argument('csvfile', help='location csv file.')
    parser.add_argument('outfile', help='output csv file name.')
    #parser.add_argument('n', help='Number of samples.')
    args = parser.parse_args()
    main(args)
