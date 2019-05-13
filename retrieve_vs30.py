import argparse
import os
import subprocess
import numpy as np
from tempfile import mkstemp

STEP_SIZE = 0.0001


def generate_grid(min_lat, max_lat, min_lon, max_lon, xy_file):
    with open(xy_file, 'w') as xy_fp:
        for lat in np.linspace(min_lat, max_lat, np.ceil((max_lat-min_lat)/STEP_SIZE)):
            for lon in np.linspace(min_lon, max_lon, np.ceil((max_lon-min_lon)/STEP_SIZE)):
                xy_fp.write("{}	{}\n".format(lon, lat))


def interpolate_grid(model_dir, xy_file, output_file):
    columns = "lon	lat	vs30\n"
    with open(output_file, "w") as output_fp:
        output_fp.write(columns)
        output_fp.flush()
        cmd = ["grdtrack", xy_file, "-nl", "-G" + str(os.path.join(model_dir, "nz_vs30_nz-specific-v19p1_100m.grd"))]
        print(" ".join(cmd))
        subprocess.call(cmd, stdout=output_fp)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "min_lat",
        type=float,
        help="The minimum latitude",
    )
    parser.add_argument(
        "max_lat",
        type=float,
        help="The maximum latitude",
    )
    parser.add_argument(
        "min_lon",
        type=float,
        help="The minimum longitude",
    )
    parser.add_argument(
        "max_lon",
        type=float,
        help="The maximum longitude",
    )
    parser.add_argument("output_file", help="path to output file")
    parser.add_argument(
        "--step_size",
        help="The maximum longitude",
        type=float,
        default=0.0001,
    )
    parser.add_argument(
        "--models_dir",
        "-m",
        help="Folder containing the models",
        default="/nesi/project/nesi00213/groundfailure/models",
    )
    args = parser.parse_args()

    xy_file = mkstemp(text=True)[1]

    min_lon, max_lon = min(args.min_lon, args.max_lon), max(args.min_lon, args.max_lon)
    min_lat, max_lat = min(args.min_lat, args.max_lat), max(args.min_lat, args.max_lat)

    generate_grid(min_lat, max_lat, min_lon, max_lon, xy_file)

    interpolate_grid(
        args.models_dir,
        xy_file,
        args.output_file,
    )
    os.remove(xy_file)


if __name__ == "__main__":
    main()
