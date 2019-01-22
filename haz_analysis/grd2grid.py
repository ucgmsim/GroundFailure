"""
Converts a csv of lon lat pgv into a grid.xml file that can be used by
the groundfailure workflow (landslide, liquefaction, PAGER)
"""

import h5py as h5
from qcore.shakemap_grid import shakemapGrid
import qcore.gmt as gmt
import qcore.geo as geo
import qcore.timeseries
import numpy as np
import os
import pandas as pd

import argparse
import errno
from qcore import shared
from qcore import utils

def get_hypocentre_loc(cnrs_file):
    with open(cnrs_file) as fp:
        line = fp.readline() # Read header line
        line = fp.readline()
        lon, lat = line.split()
        return lon, lat

parser = argparse.ArgumentParser('grd2grid')


parser.add_argument('imfile', type=str, help='Path to im file containing pgv')
parser.add_argument('stationfile', type=str, help='Path to station file containing lon/lat')
#parser.add_argument('csvfile', type=str, help='Path to csv file containing lon/lat/pgv')
parser.add_argument('run_name', type=str, help='Name of the rupture - should be unique per simulation')
parser.add_argument('output_dir', type=str, help='Directory that the output file is written to')
parser.add_argument('-m', '--magnitude', type=float, help='Moment magnitude of the rupture')
parser.add_argument('-d', '--depth', type=float, help='Depth of the hypocentre')
parser.add_argument('-c', '--srf-corners', type=str, help='Path to srf corners file to determine hypocentre location')
parser.add_argument('--dx', type=str, help="Spacing of points")
args = parser.parse_args()
print args


ifname = args.imfile
sfname = args.stationfile
run_name = args.run_name
output_dir = args.output_dir
temp_dir = os.path.join(output_dir, 'temp')
fname = os.path.join(temp_dir, os.path.basename(args.imfile.replace(".csv", "_station_merged.csv", 1)))

mag = args.magnitude
dep = args.depth
cnrs_file = args.srf_corners

if mag is None:
    mag = 0.0
if dep is None:
    dep = 0.0

if args.dx is None:
    dy = dx = '2k'
else:
    dy = dx = args.dx

utils.setup_dir(output_dir)
utils.setup_dir(temp_dir)

im_csv = pd.read_csv(ifname)
stat_csv = pd.read_csv(sfname, header=None, names=["lat","lon","station"], delim_whitespace=True)
out_csv = im_csv.merge(stat_csv)
out_csv.to_csv(fname, columns=['lat','lon','PGV'], index=False, header=False, sep=' ')

with open(fname) as f:
    lats = list()
    lons = list()
    values = list()

    for line in f:
        lon, lat, pgv = map(np.float, line.split())
        values.append((lon, lat))

values.sort(key=lambda tup: (tup[0], tup[1]))
corner1 = values[0]
corner2 = values[-1]
values.sort(key=lambda tup: (tup[1], tup[0]))
corner3 = values[0]
corner4 = values[-1]


corners = [corner3, corner1, corner4, corner2]
region = (corner1[0], corner2[0], corner3[1], corner4[1])
# region = (166.382450, 174.398790, -46.859300, -40.504500)

mask = os.path.join(temp_dir, 'modelmask.grd')

modelmask_path = os.path.join(temp_dir, 'modelpath_hr')
geo.path_from_corners(corners=corners, min_edge_points=100, output=modelmask_path)
gmt.grd_mask(modelmask_path, mask, dx=dx, dy=dy, region=region)
print "mask success"

temp_grid = os.path.join(temp_dir, 'tmp.grd')
out_grid = os.path.join(temp_dir, 'PAGER_PGV.grd')
int_xyz = os.path.join(temp_dir, 'PAGER_PGV.xyz')
gmt.table2grd(fname, temp_grid, region=region, dx=dx, dy=dy, climit=0.1)
print "table2grd success"
gmt.grdmath([temp_grid, mask, 'MUL', 0, 'AND', 0, 'MAX', '=', out_grid])

lons = set()
lats = set()
data = list()

with open(int_xyz, 'w+') as pgv_fp:
    shared.exe("grd2xyz %s" % (out_grid,) , stdout=pgv_fp)

    pgv_fp.seek(0)

    for line in pgv_fp:
        lon, lat, pgv = map(float, line.split())
        lons.add(lon)
        lats.add(lat)
        data.append((lon,lat, pgv))


grid_out = os.path.join(output_dir, 'grid.xml')

lats = list(lats)
lons = list(lons)

grd_ny = len(lats)
grd_nx = len(lons)

event_id = run_name
event_type = 'SCENARIO'

if cnrs_file is not None:
    hlon, hlat = get_hypocentre_loc(cnrs_file)
else:
    hlon = (corner1[0] + corner2[0]) / 2 
    hlat = (corner3[1] + corner4[1]) / 2
    print "putting hypocentre location in the middle of the extent"
origin_time = '2017-04-25T13:02:33.631Z'
x_min = min(lons)
x_max = max(lons)
y_min = min(lats)
y_max = max(lats)

pager_grid = shakemapGrid(grid_out)
pager_grid.write_shakemap_grid_header(event_id, event_type, mag, dep, hlat, hlon, origin_time, run_name, x_min, x_max, y_min, y_max, grd_nx,
                                      grd_ny)

data.sort(key=lambda a: (-a[1],a[0]))

for datum in data:
    lon, lat, pgv = datum
    if pgv <= 0:
        pgv = float('0')
        MMI = float('1.0')
    else:
        MMI = qcore.timeseries.pgv2MMI(pgv)
    pager_grid.write('%s %s %f %f\n'% (lon, lat, pgv, MMI))

pager_grid.write_shakemap_grid_footer()
