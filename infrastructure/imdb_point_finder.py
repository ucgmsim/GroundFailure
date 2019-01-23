#!/usr/bin/env python3

"""
For each line in a given file with longitude and latitude data append the name of the nearest station (within 10km) and
the intensity measure of the requested type for the given realisation
"""

from qcore import imdb
import argparse
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("imdb", help="IMDB file location")
parser.add_argument("input", help="Input file name")
parser.add_argument("output", help="Output file name")
parser.add_argument("realisation", help="The realisation to choose")
parser.add_argument("im", help="Intensity measure name")
args = parser.parse_args()


data = pd.read_csv(args.input, index_col=0)
data = data.assign(CLOSEST_STATION="")
data = data.assign(PGA="NaN")


for i in data.index:

    station_name, lat, long, dist = imdb.closest_station(args.imdb, data.LONG[i], data.LAT[i])
    station_name = station_name.decode("utf-8")
    if dist > 10:
        # Too far to be useful
        continue

    data.at[i, "CLOSEST_STATION"] = station_name
    PGA_realisations = imdb.station_ims(args.imdb, station_name)[args.im.encode()]
    if args.realisation in PGA_realisations:
        data.at[i, args.im] = PGA_realisations[args.realisation]

data.to_csv(args.output)
