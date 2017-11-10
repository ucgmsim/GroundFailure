#!/usr/bin/env python2
"""
This is currently tested to be working on hypocentre.
Requires: USGS groundfailure, qcore library

Takes a quake folder and using the shakemap generates liquefaction plots
for the area

Usage plot_liq.py "path/to/folder"

Writes to impact/liquefaction/ the images produced from this analysis

@date 5 Jul 2017
@author Jason Motha
@contact jason.motha@canterbury.ac.nz
"""


import glob
import os
import subprocess
import itertools
import numpy as np

import gf_common

def create_xyz_name(out_dir, run_name, model, map_type, vs30_model):
    return os.path.join(out_dir, "%s_zhu_2016_%s_%s_%s.xyz" % (run_name, model, map_type, vs30_model))
         
path, run_name, realisation = gf_common.get_path_name()

out_dir = gf_common.create_output_path(path, 'liquefaction', realisation)

gridfile = gf_common.find_gridfile(path, realisation)



plot_configs = list(itertools.product(gf_common.model_list, gf_common.map_type_list, gf_common.vs30_model_list))

for config in plot_configs:
    model, map_type, vs30_model = config

    liq_config = 'zhu_2016_%s_%s_%s.ini' % (model, map_type, vs30_model)
    model_dir = os.path.join(gf_common.sim_workflow_dir  , 'liquefaction_model')
    config_dir = os.path.join(gf_common.sim_workflow_dir  , 'config')
    liq_cmd = "python3 /usr/bin/gfail %s %s -d %s -c %s -o %s --set-bounds 'zoom, pgv, 0' --hdf5" % (liq_config, gridfile, model_dir, config_dir, out_dir)

    print 'Running liquefaction calculations'
    subprocess.call(liq_cmd, shell=True)

    h5path = glob.glob(os.path.join(out_dir, '*_%s.hdf5'% (model)))[0]

    if not os.path.exists(h5path):
        print "h5 output not found at %s" % h5path
        exit()
    
    
    xyz_path = create_xyz_name(out_dir, run_name, model, map_type, vs30_model)
    
    process_cmd = os.path.join(gf_common.sim_workflow_dir  , 'gen_gf_surface.py') + " %s -t %s -o %s" % (h5path, run_name, xyz_path)
    if model == 'coastal':
        process_cmd += " -m1"
    else:
        process_cmd += " -m2"
    if map_type == 'susceptibility':
        process_cmd += " -s"
    elif map_type == 'probability':
        process_cmd += '' #' -l0.05'        

    print 'Running conversion'
    subprocess.call(process_cmd, shell=True)

    if not os.path.exists(xyz_path):
        print "xyz file not found at %s" % xyz_path
        exit()

    gf_common.plot(out_dir, xyz_path, run_name, vs30_model, map_type, model, 'liq')


def normalise(val):
    if val < -3.2:
        return 0
    elif val < -3.15:
        return 1
    elif val < -1.95:
        return 2
    elif val < -1.15:
        return 3
    else:
        return 4
    

## plotting arithmetic distance

map_type = 'susceptibility'
model = 'arithdiff'

for vs30_model in gf_common.vs30_model_list:
    fname1 = create_xyz_name(out_dir, run_name, 'general', map_type, vs30_model)
    fname2 = create_xyz_name(out_dir, run_name, 'coastal', map_type, vs30_model)


    if os.path.exists(fname1) and os.path.exists(fname2):
        diff_out_name = create_xyz_name(out_dir, run_name, model, map_type, vs30_model)
        with open(fname1) as f1, open(fname2) as f2 , open(diff_out_name, 'w') as fout:
            print "Calculating arithmetic difference"
            unmatched = 0
            data = []
            fout.write(run_name)
            fout.write("\nGeneral - Coastal (%s, susceptibility)\n" % vs30_model)
            fout.write("polar:topo-grey1,t-30,fg-80/0/0,bg-0/0/80 1k:nns-4k,g-nearneighbor,landmask\n")
            fout.write("-1.5 1.5 1 0.5\n1 white\nArithmetic Difference\n")
            
            for __ in xrange(6):
                next(f1)
                next(f2)
            for l1, l2 in itertools.izip(f1, f2):
                lon1, lat1, v1 = l1.split()
                lon2, lat2, v2 = l2.split()
                v1 = float(v1)
                v2 = float(v2)
                while 0 and lon1 != lon2 or lat1 != lat2:
                    if lat1 == lat2:
                        if lon1 > lon2:
                            f2.next()
                        else:
                            f1.next()
                    else:
                        if lat1 > lat2:
                            f2.next()
                            f1.next()
                    unmatched += 1
                if lon1 == lon2 and lat1 == lat2:
                    v1 = normalise(v1)
                    v2 = normalise(v2)
                    val = v1 - v2
                    # if (v1 < -4.8 or v2 < -4.8) and val > -3.75:
                        # val = 0
                    if val > 0:
                        val = 1
                    elif val < 0:
                        val = -1
                    data.append(val)
                    fout.write("%s %s %f\n" % (lon1, lat1, val))
                else:
                    unmatched += 1
                            
            print "Lines without a difference: %d\n" % unmatched
            print "mean: %f, std: %f, min: %f, max: %f\n" % (np.mean(data), np.std(data, ddof=1), np.min(data), np.max(data))
            
        print diff_out_name
        gf_common.plot(out_dir, diff_out_name, run_name, vs30_model, map_type, model, 'liq')

print "Done"
