#!/usr/bin/env python3

"""
For each line in a given file with longitude and latitude data append the name of the nearest station (within 10km) and
the intensity measure of the requested type for the given realisation
"""

from os import path
from math import pow, log
import argparse
import pandas as pd
from h5py import File as h5open
from qcore import imdb, simulation_structure

scaled_ims = ["PGA", "PGV"]

magnitudes = {}
scale_functions = {
    "PGA": lambda pga, magnitude: pga * (pow(magnitude, 2.56) / pow(10, 2.24)),
    "PGV": lambda pgv, magnitude: pgv / (1 + pow(2.71828, -2 * (magnitude - 6))),
}


def scale_im(im_val, im_name, magnitude):
    if im_name in scale_functions:
        return scale_functions[im_name](im_val, magnitude)
    else:
        return im_val


def get_magnitude(sources_folder, realisation):
    if realisation not in magnitudes.keys():
        srf_path = path.join(
            sources_folder, simulation_structure.get_srf_info_location(realisation)
        )
        with h5open(srf_path, "r") as srf_file:
            magnitudes.update({realisation: srf_file.attrs["mag"]})
    return magnitudes[realisation]


def imdb_finder(
    imdb_file,
    input_file,
    output_file,
    realisations,
    intensity_measures,
    sources_folder=None,
):

    data = pd.read_csv(input_file, index_col=0, encoding="ISO-8859-1")
    data = data.assign(CLOSEST_STATION="")
    data = data.assign(
        **{
            "{}_{}{}".format(im, scaled, rel): "nan"
            for im in intensity_measures
            for scaled in (["", "scaled_"] if im in scaled_ims else [""])
            for rel in realisations
        }
    )

    for i in data.index:

        station_name, lat, lon, dist = imdb.closest_station(
            imdb_file, data.LONG[i], data.LAT[i]
        )
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
                    if sources_folder is not None and im in scaled_ims:
                        data.at[i, "{}_scaled_{}".format(im, rel)] = scale_im(
                            intensity_measure_realisations[rel], im, get_magnitude(sources_folder, rel)
                        )
                    data.at[
                        i, "{}_{}".format(im, rel)
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
    parser.add_argument(
        "-d",
        "--source_dir",
        help="The cybershake sources directory, in the data directory",
        type=str,
        default=None,
    )
    args = parser.parse_args()

    imdb_finder(
        args.imdb, args.input, args.output, args.realisation, args.im, args.source_dir
    )
