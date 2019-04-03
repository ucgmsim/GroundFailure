#!/usr/bin/env python

"""
Calculates Ground Failure (liquefaction & landslide) susceptibility & probability at points specified by the input files.
Depends on GMT binaries being in the path
"""

import argparse
import tempfile
import os
import subprocess
from enum import Enum

import pandas as pd

from USGS_models import calculations


class gfe_types(Enum):
    zhu2015 = "zhu2015"
    zhu2016 = "zhu2016"
    zhu2016_coastal = "zhu2016_coastal"
    zhu2017 = "zhu2017"
    zhu2017_coastal = "zhu2017_coastal"
    jessee2017 = "jessee2017"


def get_model_path(model_dir, model):
    """Returns path to a model file as an input argument to GMT functions"""
    return "-G" + str(os.path.join(model_dir, model))


def get_models(model_dir, gfe_type):
    """Determines the models needed for the specific GroundFailure type"""
    models = []
    if gfe_types.zhu2016 in gfe_type:
        distance_to_coast = get_model_path(model_dir, "nz_dc_km.grd")
        distance_to_rivers = get_model_path(model_dir, "nz_dr_km.grd")
        precipitation = get_model_path(model_dir, "nz_precip_fil_mm.grd")
        vs30 = get_model_path(model_dir, "nz_vs30_nz-specific-v18p4_100m.grd")
        water_table_depth = get_model_path(model_dir, "nz_wtd_fil_na_m.grd")

        models.extend(
            [
                distance_to_coast,
                distance_to_rivers,
                precipitation,
                vs30,
                water_table_depth,
            ]
        )
    if gfe_types.jessee2017 in gfe_type:
        slope = get_model_path(model_dir, "nz_grad.grd")
        lithography = get_model_path(model_dir, "nz_GLIM_replace.grd")
        land_cover = get_model_path(model_dir, "nz_globcover_replace.grd")
        cti = get_model_path(model_dir, "nz_cti_fil.grd")

        models.extend([slope, lithography, land_cover, cti])

    return models


def get_cols(df):
    """Finds the columns indicated"""
    lon_col = lat_col = None
    column_names = [str.lower(name.strip()[0:3]) for name in df.columns.values]
    if "lon" in column_names:
        lon_col = df.columns.values[column_names.index("lon")]
    if "lat" in column_names:
        lat_col = df.columns.values[column_names.index("lat")]

    if lon_col is None or lat_col is None:
        exit("invalid input - cannot find lat or lon in the input file header")

    return lat_col, lon_col


def interpolate_input_grid(model_dirs, xy_file, inputs_file, gfe_type):
    """Uses grdtrack to sample the groundfailure input grids and write their values to `inputs_file`"""
    models = get_models(model_dirs, gfe_type)
    with open(inputs_file, "w") as inputs_fp:
        columns = "lon	lat"
        if gfe_types.zhu2016 in gfe_type:
            columns = (
                columns
                + "	distance_to_coast	distance_to_rivers	precipitation	vs30	water_table_depth   dr  dc"
            )
        if "jesse2017" in gfe_type:
            columns = columns + "	slope	rock	landcover	cti"
        columns = columns + "\n"
        inputs_fp.write(columns)
        inputs_fp.flush()
        cmd = ["grdtrack", xy_file, "-nl"]
        cmd.extend(models)
        print(" ".join(cmd))
        subprocess.call(cmd, stdout=inputs_fp)


def calculate_gf(
    input_file, output_file, models_dir, gfe_type, store_susceptibility=False
):
    """Calculates groundfailure at specified locations and stores it in output_file"""
    with open(input_file, encoding="utf8", errors="backslashreplace") as in_fd:
        df = pd.read_csv(in_fd)
    df.columns = [
        x.lower() if x.lower() not in ["lon", "long"] else "lon"
        for x in list(df.columns)
    ]

    pgv_realisations = list(
        filter(
            lambda x: x if ("pgv_" in x and "pgv_scaled_" not in x) else None,
            df.columns,
        )
    )
    pgv_scaled_realisations = list(
        filter(lambda x: x if "pgv_scaled_" in x else None, df.columns)
    )
    pga_scaled_realisations = list(
        filter(lambda x: x if "pga_scaled_" in x else None, df.columns)
    )

    with tempfile.TemporaryDirectory() as tmp_folder:
        xy_file = os.path.join(tmp_folder, "points.xy")
        inputs_file = os.path.join(tmp_folder, "values.csv")

        lat_col, lon_col = get_cols(df)
        df.to_csv(
            xy_file, columns=[lon_col, lat_col], header=None, index=False, sep=","
        )

        interpolate_input_grid(models_dir, xy_file, inputs_file, gfe_type=gfe_type)
        source_data = pd.read_csv(inputs_file, delim_whitespace=True)

        trimmed_columns = ["lat", "lon"]
        columns = list(df.columns.values)
        if gfe_types.jessee2017 in gfe_type:
            source_data[
                "jesse2017_susceptibility"
            ] = calculations.calculate_jessee2017_susceptibility(
                source_data.slope,
                source_data.rock,
                source_data.cti,
                source_data.landcover,
            )
            trimmed_columns.append("jesse2017_susceptibility")
            if store_susceptibility:
                columns.append("jesse2017_susceptibility")

            for rel in pgv_realisations:
                header = "jesse2017_probability_{}".format(rel)
                source_data[header] = calculations.calculate_jessee2017_coverage(
                    df[rel], source_data.slope, source_data["jesse2017_susceptibility"]
                )
                trimmed_columns.append(header)
                columns.append(header)

        if gfe_types.zhu2015 in gfe_type:
            for rel in pga_scaled_realisations:
                header = "zhu2015_coastal_probability_{}".format(rel)
                source_data[header] = calculations.calculate_zhu2015_coverage(
                    df[rel], source_data.cti, source_data.vs30
                )
                trimmed_columns.append(header)
                columns.append(header)

        if gfe_types.zhu2016 in gfe_type:
            source_data[
                "zhu2016_susceptibility"
            ] = calculations.calculate_zhu2016_susceptibility(
                source_data.vs30,
                source_data.precipitation,
                source_data.distance_to_coast,
                source_data.distance_to_rivers,
                source_data.water_table_depth,
            )
            trimmed_columns.append("zhu2016_susceptibility")
            if store_susceptibility:
                columns.append("zhu2016_susceptibility")

            for rel in pgv_realisations:
                header = "zhu2016_probability_{}".format(rel)
                source_data[header] = calculations.calculate_zhu2016_coverage(
                    df[rel], source_data["zhu2016_susceptibility"]
                )
                trimmed_columns.append(header)
                columns.append(header)

        if gfe_types.zhu2016_coastal in gfe_type:
            for rel in pgv_realisations:
                header = "zhu2016_coastal_probability_{}".format(rel)
                source_data[header] = calculations.calculate_zhu2016_coastal_coverage(
                    df[rel],
                    source_data.vs30,
                    source_data.precip,
                    source_data.dc,
                    source_data.dr,
                )
                trimmed_columns.append(header)
                columns.append(header)

        if gfe_types.zhu2017 in gfe_type:
            source_data[
                "zhu2017_susceptibility"
            ] = calculations.calculate_zhu2016_susceptibility(
                source_data.vs30,
                source_data.precipitation,
                source_data.distance_to_coast,
                source_data.distance_to_rivers,
                source_data.water_table_depth,
            )
            trimmed_columns.append("zhu2017_susceptibility")
            if store_susceptibility:
                columns.append("zhu2017_susceptibility")
            for rel in pgv_scaled_realisations:
                header = "zhu2017_probability_{}".format(rel)
                source_data[header] = calculations.calculate_zhu2017_coverage(
                    df[rel], source_data["zhu2017_susceptibility"]
                )
                trimmed_columns.append(header)
                columns.append(header)

        if gfe_types.zhu2017_coastal in gfe_type:
            for rel in pgv_realisations:
                header = "zhu2017_coastal_probability_{}".format(rel)
                source_data[header] = calculations.calculate_zhu2017_coastal_coverage(
                    df[rel],
                    source_data.vs30,
                    source_data.precip,
                    source_data.dc,
                    source_data.dr,
                )
                trimmed_columns.append(header)
                columns.append(header)

        source_data_trimmed = source_data[trimmed_columns]
        df = df.merge(
            source_data_trimmed, left_on=[lat_col, lon_col], right_on=["lat", "lon"]
        )
    df.to_csv(output_file, columns=columns, index=False, sep=",")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input_file",
        help="CSV containing lat, lon values."
        "Must have a header column starting with lat, lon)",
    )
    parser.add_argument("output_file", help="path to output file")
    parser.add_argument(
        "--gfe_type",
        "-g",
        choices=[x.value for x in gfe_types],
        required=True,
        nargs="+",
    )
    parser.add_argument(
        "--susceptibility", "-s", help="Flag indicating to store susceptibility"
    )
    parser.add_argument(
        "--models_dir",
        "-m",
        help="Folder containing the models",
        default="/nesi/project/nesi00213/groundfailure/models",
    )
    args = parser.parse_args()

    calculate_gf(
        args.input_file,
        args.output_file,
        args.models_dir,
        [gfe_types(x) for x in args.gfe_type],
        args.susceptibility,
    )


if __name__ == "__main__":
    main()
