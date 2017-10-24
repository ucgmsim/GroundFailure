#!/usr/bin/env python2
"""
This is currently tested to be working: nowhere
Requires: USGS groundfailure,

Takes a quake folder and using the shakemap generates landslide plots for the area

Usage plot_ls.py "path/to/folder"

Writes to impact/landslide the images produced from this analysis

@date 6 Oct 2017
@author Jason Motha
@contact jason.motha@canterbury.ac.nz
"""

import glob
import argparse
import subprocess
import os

import gf_common

def create_xyz_name(out_dir, run_name, map_type):
    return os.path.join(out_dir, "%s_jessee_2017_%s.xyz" % (run_name,map_type))

def __main__():
    path, run_name = gf_common.get_path_name()

    out_dir = os.path.join(path, 'Impact/Landslide/')

    gridfile = gf_common.find_gridfile(path)

    for map_type in gf_common.map_type_list:
        config = 'jessee_2017_%s.ini' % (map_type)
        
        model_dir = os.path.join(gf_common.sim_workflow_dir  , 'landslide_model')
        config_dir = os.path.join(gf_common.sim_workflow_dir  , 'config')
        ls_cmd = "python3 /usr/bin/gfail %s %s -d %s -c %s -o %s --set-bounds 'zoom, pgv, 0' --hdf5" % (config, gridfile, model_dir, config_dir, out_dir)

        print 'Running landslide calculations'
        print ls_cmd
        subprocess.call(ls_cmd, shell=True)
        
        h5path = glob.glob(os.path.join(out_dir, '*.hdf5'))[0]

        if not os.path.exists(h5path):
            print "h5 output not found at %s" % h5path
            exit()
        
        
        xyz_path = create_xyz_name(out_dir, run_name, map_type)
        
        process_cmd = os.path.join(gf_common.sim_workflow_dir  , 'gen_gf_surface.py') + " %s -t %s -o %s -type ls" % (h5path, run_name, xyz_path)
        
        if map_type == 'susceptibility':
            process_cmd += " -s" 

        print 'Running conversion'
        subprocess.call(process_cmd, shell=True)
        
        gf_common.plot(out_dir, xyz_path, run_name, "", map_type, "", 'landslide')


__main__()
