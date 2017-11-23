import h5py as h5
from qcore.shakemap_grid import shakemapGrid
import qcore.gmt as gmt
import qcore.geo as geo
import qcore.timeseries
import numpy as np
import os

import argparse
import errno


def create_dir(directory):
    """Function to create the Figures dir if it doesn't exist
    Inputs:
        parms - the parameters
    Outputs:
        None
    """
    try:
        os.makedirs(directory)
        print 'Creating dir %s ' % (directory)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise

        print 'Not Creating dir %s. Already exists' % (directory)
        pass

parser = argparse.ArgumentParser('csv2grid')

parser.add_argument('csvfile', type=str)
parser.add_argument('run_name', type=str)
parser.add_argument('output_dir', type=str)
args = parser.parse_args()

fname = args.csvfile
run_name = args.run_name
output_dir = args.output_dir
temp_dir = os.path.join(output_dir, 'temp')

create_dir(output_dir)
create_dir(temp_dir)

with open(fname) as f:
    lats = list()
    lons = list()
    values = list()

    for line in f:
        lon, lat, ___ = map(np.float, line.split())
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

dy = dx = '2k'

modelmask_path = os.path.join(temp_dir, 'modelpath_hr')
geo.path_from_corners(corners=corners, min_edge_points=100, output=modelmask_path)
gmt.grd_mask(modelmask_path, mask, dx=dx, dy=dy, region=region)
print "mask success"

temp_grid = os.path.join(temp_dir, 'tmp.grd')
out_grid = os.path.join(temp_dir, 'PAGER_PGV.grd')
gmt.table2grd(fname, temp_grid, region=region, dx=dx, dy=dy, climit=0.1)
print "table2grd sucess"
gmt.grdmath([temp_grid, mask, 'MUL', 0, 'AND', 0, 'MAX', '=', out_grid], region=region, dx=dx, dy=dy)

grd_pgv = h5.File(out_grid)
grid_out = os.path.join(output_dir, 'grid.xml')
#grd_mmi = h5.File('/PAGER_MMI.grd')
# lat stored min -> max but pager requires top -> bottom
lons = grd_pgv['lon'][...]
lats = grd_pgv['lat'][...]
pgvs = grd_pgv['z'][...]
#mmis = grd_mmi['z'][...]
grd_ny, grd_nx = pgvs.shape
grd_pgv.close()
#grd_mmi.close()


event_id = run_name
event_type = 'SCENARIO'
mag = 0
dep = 0

hlon, hlat = '-43.5704072732', '172.689081167'
origin_time = '2017-04-25T13:02:33.631Z'
x_min = lons[0]
x_max = lons[-1]
y_min = lats[0]
y_max = lats[-1]

pager_grid = shakemapGrid(grid_out)
pager_grid.write_shakemap_grid_header(event_id, event_type, mag, dep, hlat, hlon, origin_time, run_name, x_min, x_max, y_min, y_max, grd_nx,
                                      grd_ny)
for a in xrange(len(lats) - 1, - 1, - 1):
    for b in xrange(len(lons)):
        pgv = np.float(pgvs[a, b])
        if pgv <= 0:
            pgv = float('0')
            MMI = float('0')
        else:
            MMI = qcore.timeseries.pgv2MMI(pgv)
        pager_grid.write('%s %s %f %f\n' \
                         % (lons[b], lats[a], pgv, MMI))
pager_grid.write_shakemap_grid_footer()

