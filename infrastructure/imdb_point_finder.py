#!/usr/bin/env python3

"""
For each line in a given file with longitude and latitude data append the name of the nearest station (within 10km) and
the intensity measure of the requested type for the given realisation
"""

from qcore import imdb
import argparse
import pandas as pd


def imdb_finder(imdb_file, input_file, output_file, realisation, intensity_measure):

    data = pd.read_csv(input_file, index_col=0, encoding="ISO-8859-1")
    data = data.assign(CLOSEST_STATION="")
    data = data.assign(INTENSITY_MEASURE="nan")

    for i in data.index:

        station_name, lat, lon, dist = imdb.closest_station(
            imdb_file, data.LONG[i], data.LAT[i]
        )
        station_name = station_name.decode("utf-8")
        if dist > 10:
            # Too far to be useful
            continue
        data.at[i, "CLOSEST_STATION"] = station_name
        intensity_measure_realisations = imdb.station_ims(imdb_file, station_name)[
            intensity_measure
        ]
        if realisation in intensity_measure_realisations:
            data.at[i, "INTENSITY_MEASURE"] = intensity_measure_realisations[
                realisation
            ]

    data.to_csv(output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("imdb", help="IMDB file location")
    parser.add_argument("input", help="Input file name")
    parser.add_argument("output", help="Output file name")
    parser.add_argument("realisation", help="The realisation to choose")
    parser.add_argument("im", help="Intensity measure name")
    args = parser.parse_args()

    imdb_finder(args.imdb, args.input, args.output, args.realisation, args.im)
