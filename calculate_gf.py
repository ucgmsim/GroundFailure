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

LON = "lon"
LAT = "lat"
JESSEE_2017_SUSCEPTIBILITY = "jessee2017_susceptibility"
ZHU_2017_COASTAL_SUSCEPTIBILITY = "zhu2017_coastal_susceptibility"
ZHU_2017_SUSCEPTIBILITY = "zhu2017_susceptibility"
ZHU_2016_COASTAL_SUSCEPTIBILITY = "zhu2016_coastal_susceptibility"
ZHU_2016_SUSCEPTIBILITY = "zhu2016_susceptibility"
ZHU_2015_SUSCEPIBILITY = "zhu2015_susceptibility"


class params(Enum):
    DISTANCE_TO_COAST = "nz_dc_km.grd"
    DISTANCE_TO_RIVERS = "nz_dr_km.grd"
    PRECIPITATION = "nz_precip_fil_mm.grd"
    VS30 = "nz_vs30_nz-specific-v19p1_100m.grd"
    WATER_TABLE_DEPTH = "nz_wtd_fil_na_m.grd"
    SLOPE = "nz_grad.grd"
    ROCK = "nz_GLIM_replace.grd"
    LANDCOVER = "nz_globcover_replace.grd"
    CTI = "nz_cti_fil.grd"


class gfe_types(Enum):
    zhu2015 = "zhu2015", (params.CTI, params.VS30)
    zhu2016 = (
        "zhu2016",
        (
            params.DISTANCE_TO_COAST,
            params.DISTANCE_TO_RIVERS,
            params.PRECIPITATION,
            params.VS30,
            params.WATER_TABLE_DEPTH,
        ),
    )
    zhu2016_coastal = (
        "zhu2016_coastal",
        (
            params.DISTANCE_TO_COAST,
            params.DISTANCE_TO_RIVERS,
            params.PRECIPITATION,
            params.VS30,
        ),
    )
    zhu2017 = (
        "zhu2017",
        (
            params.DISTANCE_TO_COAST,
            params.DISTANCE_TO_RIVERS,
            params.PRECIPITATION,
            params.VS30,
            params.WATER_TABLE_DEPTH,
        ),
    )
    zhu2017_coastal = (
        "zhu2017_coastal",
        (
            params.DISTANCE_TO_COAST,
            params.DISTANCE_TO_RIVERS,
            params.PRECIPITATION,
            params.VS30,
        ),
    )
    jessee2017 = (
        "jessee2017",
        (params.SLOPE, params.ROCK, params.LANDCOVER, params.CTI),
    )

    def __new__(cls, str_value, columns):
        obj = object.__new__(cls)
        obj.str_value = str_value
        obj.columns = columns
        return obj


def get_model_path(model_dir, model):
    """Returns path to a model file as an input argument to GMT functions"""
    return "-G" + str(os.path.join(model_dir, model))


def get_required_params(gfe_type):
    params = set()
    for gfe in gfe_type:
        params.update(gfe.columns)
    return sorted(list(params), key=lambda x: x.name)


def get_models(model_dir, gfe_type):
    """Determines the models needed for the specific GroundFailure type"""
    models = []
    for model_type in get_required_params(gfe_type):
        models.append(get_model_path(model_dir, model_type.value))
    return models


def get_cols(df):
    """Finds the columns indicated"""
    lon_col = lat_col = None
    column_names = [str.lower(name.strip()[0:3]) for name in df.columns.values]
    if LON in column_names:
        lon_col = df.columns.values[column_names.index(LON)]
    if LAT in column_names:
        lat_col = df.columns.values[column_names.index(LAT)]

    if lon_col is None or lat_col is None:
        exit("invalid input - cannot find lat or lon in the input file header")

    return lat_col, lon_col


def interpolate_input_grid(model_dirs, xy_file, inputs_file, gfe_type):
    """Uses grdtrack to sample the groundfailure input grids and write their values to `inputs_file`"""
    models = get_models(model_dirs, gfe_type)
    with open(inputs_file, "w") as inputs_fp:
        columns = "	".join(param.name for param in get_required_params(gfe_type))
        columns = "{}	{}	".format(LON, LAT) + columns + "\n"
        inputs_fp.write(columns)
        inputs_fp.flush()
        cmd = ["gmt", "grdtrack", xy_file, "-nl"]
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
        x.lower() if x.lower() not in [LON, "long"] else LON for x in list(df.columns)
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

        trimmed_columns = [LAT, LON]
        columns = list(df.columns.values)
        if gfe_types.jessee2017 in gfe_type:
            source_data[
                JESSEE_2017_SUSCEPTIBILITY
            ] = calculations.calculate_jessee2017_susceptibility(
                source_data[params.SLOPE.name],
                source_data[params.ROCK.name],
                source_data[params.CTI.name],
                source_data[params.LANDCOVER.name],
            )
            trimmed_columns.append(JESSEE_2017_SUSCEPTIBILITY)
            if store_susceptibility:
                columns.append(JESSEE_2017_SUSCEPTIBILITY)

            for rel in pgv_realisations:
                header = "jessee2017_probability_{}".format(rel)
                source_data[header] = calculations.calculate_jessee2017_coverage(
                    df[rel],
                    source_data[params.SLOPE.name],
                    source_data[JESSEE_2017_SUSCEPTIBILITY],
                )
                trimmed_columns.append(header)
                columns.append(header)

        if gfe_types.zhu2015 in gfe_type:
            source_data[
                ZHU_2015_SUSCEPIBILITY
            ] = calculations.calculate_zhu2015_susceptibility(
                source_data[params.CTI.name], source_data[params.VS30.name]
            )
            trimmed_columns.append(ZHU_2015_SUSCEPIBILITY)
            if store_susceptibility:
                columns.append(ZHU_2015_SUSCEPIBILITY)
            for rel in pga_scaled_realisations:
                header = "zhu2015_coastal_probability_{}".format(rel)
                source_data[header] = calculations.calculate_zhu2015_coverage(
                    df[rel], source_data[ZHU_2015_SUSCEPIBILITY]
                )
                trimmed_columns.append(header)
                columns.append(header)

        if gfe_types.zhu2016 in gfe_type:
            source_data[
                ZHU_2016_SUSCEPTIBILITY
            ] = calculations.calculate_zhu2016_susceptibility(
                source_data[params.VS30.name],
                source_data[params.PRECIPITATION.name],
                source_data[params.DISTANCE_TO_COAST.name],
                source_data[params.DISTANCE_TO_RIVERS.name],
                source_data[params.WATER_TABLE_DEPTH.name],
            )
            trimmed_columns.append(ZHU_2016_SUSCEPTIBILITY)
            if store_susceptibility:
                columns.append(ZHU_2016_SUSCEPTIBILITY)

            for rel in pgv_realisations:
                header = "zhu2016_probability_{}".format(rel)
                source_data[header] = calculations.calculate_zhu2016_coverage(
                    df[rel], source_data[ZHU_2016_SUSCEPTIBILITY]
                )
                trimmed_columns.append(header)
                columns.append(header)

        if gfe_types.zhu2016_coastal in gfe_type:
            header = ZHU_2016_COASTAL_SUSCEPTIBILITY
            source_data[header] = calculations.calculate_zhu2016_coastal_susceptability(
                source_data[params.VS30.name],
                source_data[params.PRECIPITATION.name],
                source_data[params.DISTANCE_TO_COAST.name],
                source_data[params.DISTANCE_TO_RIVERS.name],
            )
            trimmed_columns.append(header)
            if store_susceptibility:
                columns.append(header)
            for rel in pgv_realisations:
                header = "zhu2016_coastal_probability_{}".format(rel)
                source_data[header] = calculations.calculate_zhu2016_coastal_coverage(
                    df[rel], source_data[ZHU_2016_COASTAL_SUSCEPTIBILITY]
                )
                trimmed_columns.append(header)
                columns.append(header)

        if gfe_types.zhu2017 in gfe_type:
            source_data[
                ZHU_2017_SUSCEPTIBILITY
            ] = calculations.calculate_zhu2017_susceptibility(
                source_data[params.VS30.name],
                source_data[params.PRECIPITATION.name],
                source_data[params.DISTANCE_TO_COAST.name],
                source_data[params.DISTANCE_TO_RIVERS.name],
                source_data[params.WATER_TABLE_DEPTH.name],
            )
            trimmed_columns.append(ZHU_2017_SUSCEPTIBILITY)
            if store_susceptibility:
                columns.append(ZHU_2017_SUSCEPTIBILITY)
            for rel in pgv_scaled_realisations:
                header = "zhu2017_probability_{}".format(rel)
                source_data[header] = calculations.calculate_zhu2017_coverage(
                    df[rel], source_data[ZHU_2017_SUSCEPTIBILITY]
                )
                trimmed_columns.append(header)
                columns.append(header)

        if gfe_types.zhu2017_coastal in gfe_type:
            header = ZHU_2017_COASTAL_SUSCEPTIBILITY
            source_data[header] = calculations.calculate_zhu2017_coastal_susceptibility(
                source_data[params.VS30.name],
                source_data[params.PRECIPITATION.name],
                source_data[params.DISTANCE_TO_COAST.name],
                source_data[params.DISTANCE_TO_RIVERS.name],
            )
            trimmed_columns.append(header)
            if store_susceptibility:
                columns.append(header)
            for rel in pgv_realisations:
                header = "zhu2017_coastal_probability_{}".format(rel)
                source_data[header] = calculations.calculate_zhu2017_coastal_coverage(
                    df[rel], source_data[ZHU_2017_COASTAL_SUSCEPTIBILITY]
                )
                trimmed_columns.append(header)
                columns.append(header)

        #round the latitudes / longitudes to remove float error in the merge
        df[lat_col] = df[lat_col].round(9)
        df[lon_col] = df[lon_col].round(9)
        source_data[LAT] = source_data[LAT].round(9)
        source_data[LON] = source_data[LON].round(9)

        source_data_trimmed = source_data  #  [trimmed_columns]
        df = df.merge(
            source_data_trimmed, left_on=[lat_col, lon_col], right_on=[LAT, LON], how='left'
        )
    #df.drop_duplicates(subset=[LAT, LON], inplace=True)
    df.to_csv(output_file, columns=columns, index=False, sep=",")
    df.to_csv(output_file, index=False, sep=",")


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
        choices=[x.str_value for x in gfe_types],
        required=True,
        nargs="+",
    )
    parser.add_argument(
        "--susceptibility",
        "-s",
        help="Flag indicating to store susceptibility",
        action="store_true",
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
        [gfe_types[x] for x in args.gfe_type],
        args.susceptibility,
    )


if __name__ == "__main__":
    main()
