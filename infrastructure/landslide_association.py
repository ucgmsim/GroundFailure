#!/usr/bin/env python

"""
Takes a csv file containing a list of infrstructure latitudes and longitudes then associates them with the nearest landlside if one is available.
CSV must have headers named LAT and LONG
"""

import argparse
import numpy as np
from mapio.multihaz import MultiHazardGrid
from mapio.dataset import DataSetException
import pandas as pd

def main(args):
    ls_file = args.hdf5file
    csv_file = args.csvfile

    # Load data
    grid = MultiHazardGrid.load(ls_file)
    keys = list(grid.getLayerNames())
    data = grid.getData()[keys[0]]
    
    csv_data = pd.read_csv(csv_file)
    csv_data = csv_data.assign(LANDSLIDE="")
    
    for i in range(len(csv_data)):
        lat, lon = csv_data.iloc[i][["LAT","LONG"]]
        try:
            csv_data.at[i, "LANDSLIDE"] = data.getValue(lat, lon)
        except DataSetException as e:
            #Outside the grid, so no valid result
            csv_data.at[i, "LANDSLIDE"] = "NaN"
    
    csv_data.to_csv(args.outfile)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('hdf5file', help='groundfailure hdf file.')
    parser.add_argument('csvfile', help='location csv file.')
    parser.add_argument('outfile', help='output csv file name.')
    args = parser.parse_args()
    main(args)
