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
from qcore import simulation_structure
import numpy as np

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


def closest_station(lon, lat, im_csv: pd.DataFrame):

    d = (
        np.sin(np.radians(im_csv.lat - lat) / 2.0) ** 2
        + np.cos(np.radians(lat))
        * np.cos(np.radians(im_csv.lat))
        * np.sin(np.radians(im_csv.lon - lon) / 2.0) ** 2
    )
    r = 6378.139 * 2.0 * np.arctan2(np.sqrt(d), np.sqrt(1 - d))
    row = im_csv.iloc[np.argmin(r)]
    return row['station'], row['lat'], row['lon'], np.min(r)


def im_csv_finder(
    im_csv_file,
    station_file,
    input_file,
    output_file,
    realisation,
    intensity_measures,
    magnitude=None,
):

    data = pd.read_csv(input_file, index_col=0, encoding="ISO-8859-1")
    data = data.assign(CLOSEST_STATION="")
    data = data.assign(
        **{
            "{}_{}{}".format(im, scaled, realisation): "nan"
            for im in intensity_measures
            for scaled in (["", "scaled_"] if im in scaled_ims else [""])
        }
    )

    im_csv_data = pd.read_csv(im_csv_file)
    station_file_data = pd.read_csv(station_file, index_col=2, sep=" ", names=("lon", "lat", "station"))

    station_data = im_csv_data.join(station_file_data, on="station", how="left")

    for i in data.index:

        station_name, lat, lon, dist = closest_station(
            data.LONG[i], data.LAT[i], station_data
        )
        if dist > 10:
            # Too far to be useful
            continue
        data.at[i, "CLOSEST_STATION"] = station_name

        for im in intensity_measures:

            if magnitude is not None and im in scaled_ims:
                data.at[i, "{}_scaled_{}".format(im, realisation)] = scale_im(
                    station_data.loc(station_name, im), im, magnitude
                )
            data.at[
                i, "{}_{}".format(im, realisation)
            ] = station_data.loc(station_name, im)

    data.to_csv(output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("im_csv", help="im_csv file location")
    parser.add_argument("station_file", help="station file location")
    parser.add_argument("input", help="Input file name")
    parser.add_argument("output", help="Output file name")
    parser.add_argument(
        "realisation",
        help="The realisation to choose",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--im", help="Intensity measure name", nargs="+", type=str, required=True
    )
    parser.add_argument(
        "--magnitude",
        help="The magnitude of the event",
        type=float,
        default=None,
    )
    args = parser.parse_args()

    im_csv_finder(
        args.im_csv, args.station_file, args.input, args.output, args.realisation, args.im, args.magnitude
    )
