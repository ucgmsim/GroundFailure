#!/usr/bin/env python3

"""
For each line in a given file with longitude and latitude data append the name of the nearest station (within 10km) and
the intensity measure of the requested type for the given realisation
"""

from qcore import imdb
import argparse
import pandas as pd


def imdb_finder(imdb_file, input_file, output_file, realisations, intensity_measures):

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

        for im in intensity_measures:
            intensity_measure_realisations = imdb.station_ims(
                imdb_file, station_name, im
            )
            for rel in realisations:
                if rel in intensity_measure_realisations:
                    data.at[
                        i, "{}_{}".format(im.decode("utf-8"), rel.decode("utf-8"))
                    ] = intensity_measure_realisations[rel]

    data.to_csv(output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("imdb", help="IMDB file location")
    parser.add_argument("input", help="Input file name")
    parser.add_argument("output", help="Output file name")
    parser.add_argument(
        "--realisation",
        help="The realisation to choose",
        nargs="+",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--im", help="Intensity measure name", nargs="+", type=str, required=True
    )
    args = parser.parse_args()

    imdb_finder(
        args.imdb,
        args.input,
        args.output,
        [rel.encode("utf-8") for rel in args.realisation],
        [im.encode("utf-8") for im in args.im],
    )
