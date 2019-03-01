import argparse
import tempfile
import os
import subprocess

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def get_model_path(model_dir):
    distance_to_coast = "-Gnz_dc_km.grd"
    distance_to_rivers = "-Gnz_dr_km.grd"
    precipitation = "-Gnz_precip_fil_mm.grd"
    vs30 = "-Gnz_vs30_nz-specific-v18p4_100m.grd"
    water_table_depth = "-Gnz_wtd_fil_na_m.grd"
    return [distance_to_coast, distance_to_rivers, precipitation, vs30, water_table_depth]


def get_cols(df):
    lat_col = 1
    lon_col = 0
    column_names = [str.lower(name[0:3]) for name in df.columns.values]
    if 'lon' in column_names:
        lon_col = df.columns.values[column_names.index('lon')]
    if 'lat' in column_names:
        lat_col = df.columns.values[column_names.index('lat')]

    return lat_col, lon_col


def get_input_values(model_dirs, xy_file, inputs_file, gfe_type='zhu_2017'):
    models = get_model_path(model_dirs)
    with open(inputs_file, 'w') as inputs_fp:
        inputs_file.write("lat	lon	distance_to_coast	distance_to_rivers	precipitation	vs30	water_table_depth\n")
        cmd = ["grdtrack", xy_file, "-nl"]
        cmd.extend(models)
        subprocess.call(cmd, shell=True, stdout=inputs_fp)


def calculate_gf():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help="CSV containing lat, lon values."
                                           "Must have a header column starting with lat, lon)")
    parser.add_argument('output_file', help="path to output file")
    parser.add_argument('--gfe_type', '-g', choices=['ls', 'liq'], required=True)
    parser.add_argument('--suscesptibility', '-s', help="Flag indicating to store susceptibility")
    parser.add_argument('--im_file', '-i', help="File containing an IM_csv for probability calculations")
    parser.add_argument('--models_dir', '-m', help="Folder containing the models")

    args = parser.parse_args()

    df = pd.read_csv(args.input_file)

    with tempfile.TemporaryDirectory as tmp_folder:
        xy_file = os.path.join(tmp_folder, 'points.xy')
        inputs_file = os.path.join(tmp_folder, 'values.csv')

        lat_col, lon_col = get_cols(df)
        df.to_csv(xy_file, columns=[lat_col, lon_col], header=None, index=False, sep=',')

        get_input_values(args.models_dir, xy_file, inputs_file)
        source_data = pd.read_csv(inputs_file, delim_whitespace=True)
        source_data['liquefaction_susceptibility'] = (8.801 +
                                             np.log(source_data.vs30) * -1.918 +
                                             source_data.precipitation * 0.0005408 +
                                             np.minimum(source_data.distance_to_coast, source_data.distance_to_rivers) * -0.2054 +
                                             source_data.water_table_depth * -0.0333)

        source_data_trimmed = source_data[['lat', 'lon', 'liquefaction_susceptibility']]
        df = df.merge(source_data_trimmed, left_on=[lat_col, lon_col], right_on=['lat', 'lon'])
    df.to_csv(args.output_file)


if __name__ == 'main':
    calculate_gf()