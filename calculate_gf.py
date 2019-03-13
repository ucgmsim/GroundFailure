import argparse
import tempfile
import os
import subprocess

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def get_model_path(model):
    return "-G" + str(os.path.join('/home/nesi00213/groundfailure/models', model))

def get_models(model_dir, gfe_type):
    models = []
    if 'zhu2016' in gfe_type:
        distance_to_coast = get_model_path("nz_dc_km.grd")
        distance_to_rivers = get_model_path("nz_dr_km.grd")
        precipitation = get_model_path("nz_precip_fil_mm.grd")
        vs30 = get_model_path("nz_vs30_nz-specific-v18p4_100m.grd")
        water_table_depth = get_model_path("nz_wtd_fil_na_m.grd")
        
        models.extend([distance_to_coast, distance_to_rivers, precipitation, vs30, water_table_depth])
    if 'jesse2017' in gfe_type:
        slope = get_model_path("nz_grad.grd")
        lithography = get_model_path("nz_GLIM_replace.grd")
        land_cover = get_model_path("nz_globcover_replace.grd")
        cti = get_model_path("nz_cti_fil.grd")
        
        models.extend([slope, lithography, land_cover, cti])
        
    return models


def get_cols(df):
    lon_col = lat_col = None
    column_names = [str.lower(name.strip()[0:3]) for name in df.columns.values]
    if 'lon' in column_names:
        lon_col = df.columns.values[column_names.index('lon')]
    if 'lat' in column_names:
        lat_col = df.columns.values[column_names.index('lat')]

    if lon_col is None or lat_col is None:
        exit("invalid input")

    return lat_col, lon_col


def get_input_values(model_dirs, xy_file, inputs_file, gfe_type):
    models = get_models(model_dirs, gfe_type)
    with open(inputs_file, 'w') as inputs_fp:
        columns = "lon	lat"
        if 'zhu2016' in gfe_type:
            columns = columns + "	distance_to_coast	distance_to_rivers	precipitation	vs30	water_table_depth"
        if 'jesse2017' in gfe_type:
            columns = columns + "	slope	rock	landcover	cti"
        columns = columns + '\n'
        inputs_fp.write(columns)
        inputs_fp.flush()
        cmd = ["grdtrack", xy_file, "-nl"]
        cmd.extend(models)
        print(' '.join(cmd))
        subprocess.call(cmd, stdout=inputs_fp)


def calculate_gf():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help="CSV containing lat, lon values."
                                           "Must have a header column starting with lat, lon)")
    parser.add_argument('output_file', help="path to output file")
    parser.add_argument('--gfe_type', '-g', choices=['zhu2016', 'jesse2017'], required=True, nargs="+")
    parser.add_argument('--suscesptibility', '-s', help="Flag indicating to store susceptibility")
    parser.add_argument('--im_file', '-i', help="File containing an IM_csv for probability calculations")
    parser.add_argument('--models_dir', '-m', help="Folder containing the models")

    args = parser.parse_args()

    in_fd = open(args.input_file, encoding='utf8', errors = 'backslashreplace')
    df = pd.read_csv(in_fd)

    with tempfile.TemporaryDirectory() as tmp_folder:
        xy_file = os.path.join(tmp_folder, 'points.xy')
        inputs_file = os.path.join(tmp_folder, 'values.csv')

        lat_col, lon_col = get_cols(df)
        df.to_csv(xy_file, columns=[lon_col, lat_col], header=None, index=False, sep=',')

        get_input_values(args.models_dir, xy_file, inputs_file, gfe_type=args.gfe_type)
        source_data = pd.read_csv(inputs_file, delim_whitespace=True)
        
        trimmed_columns = ['lat', 'lon']
        columns = list(df.columns.values)
        if 'jesse2017' in args.gfe_type:
            source_data['jesse2017_susceptibility'] = (-6.3 +
                                             np.arctan(source_data.slope) * 0.06 * 180 / np.pi +
                                             source_data.rock * 1 +
                                             source_data.cti * 0.03 +
                                             source_data.landcover * 1.0)
            columns.append('jesse2017_susceptibility')
            trimmed_columns.append('jesse2017_susceptibility')
        if 'zhu2016' in args.gfe_type:
            source_data['zhu2016_susceptibility'] = (8.801 +
                                             np.log(source_data.vs30) * -1.918 +
                                             source_data.precipitation * 0.0005408 +
                                             np.minimum(source_data.distance_to_coast, source_data.distance_to_rivers) * -0.2054 +
                                             source_data.water_table_depth * -0.0333)
            columns.append('zhu2016_susceptibility')
            trimmed_columns.append('zhu2016_susceptibility')
        source_data_trimmed = source_data[trimmed_columns]
        df = df.merge(source_data_trimmed, left_on=[lat_col, lon_col], right_on=['lat', 'lon'])
    df.to_csv(args.output_file, columns=columns, index=False, sep=',')


if __name__ == '__main__':
    calculate_gf()
