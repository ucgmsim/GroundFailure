#!/usr/bin/env python

"""
Takes a folder of folders containing ground failure events and a folder of location csv files and cross references them,
finding the nearest ground failure to each location. Also uses the imdb to find the PGA and PGV at that location.
"""

import argparse
import os
import sys
import multiprocessing

import imdb_point_finder, usgs_point_finder
from qcore import imdb


def main(imdb_fname, landslide_fname, liquefaction_fname, files, ims, realisation=None):
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count() // 2)

    if imdb_fname != "None":

        # Current constant for realisation names. Still need to find the number of realisations to get the full name of
        # the realisation
        # Will need to be updated if naming scheme changes
        realisation_constant = "_HYP01-"

        sims = list(map(lambda x: x.decode("utf-8"), imdb.simulations(imdb_fname)))
        imdb_ims = list(map(lambda x: x.decode("utf-8"), imdb.ims(imdb_fname)))
        temp_ims = [im for im in ims]

        for im in temp_ims:
            if im not in imdb_ims:
                print(
                    "No im found for {}, please ensure you have correct spelling and capitalisation.".format(
                        im
                    )
                )
                ims.remove(im)

        for input_file in files:

            # Find the name of the realisation
            if realisation is None:
                if landslide_fname != "None":
                    realisation_prefix = (
                        landslide_fname.split("/")[-1].split("_")[0]
                        + realisation_constant
                    )
                elif liquefaction_fname != "None":
                    realisation_prefix = (
                        liquefaction_fname.split("/")[-1].split("_")[0]
                        + realisation_constant
                    )
                else:
                    print("Unable to determine realisation, aborting.")
                    continue
            restricted_realisations = [
                x for x in sims if x.startswith(realisation_prefix)
            ]

            if len(restricted_realisations) > 1:
                print(
                    "Too many possible realisations for file '{}', not attempting to find imdb values".format(
                        input_file
                    )
                )
                continue

            realisation = restricted_realisations[0]

            # List of ims to use.
            output = os.path.join(args.output, os.path.basename(input_file))
            pool.apply_async(
                imdb_point_finder.imdb_finder,
                (
                    imdb_fname,
                    input_file,
                    output,
                    realisation.encode(),
                    [im.encode() for im in ims],
                ),
            )

    if landslide_fname != "None":
        for input_file in files:
            output = os.path.join(
                args.output,
                os.path.basename(input_file.replace(".csv", "_landslide.csv")),
            )
            pool.apply_async(
                usgs_point_finder.ground_failure_finder,
                (landslide_fname, input_file, output),
            )

    if liquefaction_fname != "None":
        for input_file in files:
            output = os.path.join(
                args.output,
                os.path.basename(input_file.replace(".csv", "_liquefaction.csv")),
            )
            pool.apply_async(
                usgs_point_finder.ground_failure_finder,
                (liquefaction_fname, input_file, output),
            )

    pool.close()
    pool.join()
    print("All tasks completed")


if __name__ == "__main__":

    parser = argparse.ArgumentParser("masterInfra")
    parser.add_argument("imdb", type=str, help="Path to imdb file. May be None")
    parser.add_argument(
        "landslide", type=str, help="Path to landslide hdf5 file. May be None"
    )
    parser.add_argument(
        "liquefaction", type=str, help="Path to liquefaction hdf5 file. May be None"
    )
    parser.add_argument(
        "output", type=str, help="The folder to put all output files in."
    )
    parser.add_argument(
        "-i",
        "--intensity_measures",
        type=str,
        dest="ims",
        nargs="+",
        default=["PGA"],
        help="The intensity measures to take from imdb.",
    )

    files = parser.add_mutually_exclusive_group(required=True)
    files.add_argument(
        "-g",
        "--infrastructure_folder",
        type=str,
        help="Name of the rupture - should be unique per simulation",
    )
    files.add_argument(
        "-f",
        "--infrastructure_files",
        type=str,
        dest="files",
        nargs=argparse.REMAINDER,
        help="A list of infrastructure files to be processed",
    )

    if ("-f" not in sys.argv) and ("-g" not in sys.argv) and len(sys.argv) > 1:
        sys.argv.insert(-1, "-g")

    print(sys.argv)

    args = parser.parse_args()

    files = ""
    if args.files:
        files = args.files
    else:
        folder = args.infrastructure_folder
        files = list(map(lambda x: os.path.join(folder, x), os.listdir(folder)))

    main(args.imdb, args.landslide, args.liquefaction, files, args.ims)
