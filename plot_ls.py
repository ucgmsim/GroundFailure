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
import sys

import gf_common

def create_xyz_name(out_dir, run_name, map_type):
    return os.path.join(out_dir, "%s_jessee_2017_%s.xyz" % (run_name,map_type))

def __main__():
    path, run_name, realisation = gf_common.get_path_name()

    out_dir = gf_common.create_output_path(path, 'Landslide', realisation)
    non_realisation_path = gf_common.create_output_path(path, 'Landslide', None)

    gridfile = gf_common.find_gridfile(path, realisation)

    script_location = os.path.realpath(sys.argv[0])
    script_folder = os.path.dirname(script_location)
    gen_gf_surface_location = os.path.join(script_folder, gf_common.gen_gf_surface_name)
    if not os.path.exists(gen_gf_surface_location):
        gen_gf_surface_location = os.path.join(gf_common.sim_workflow_dir, gf_common.gen_gf_surface_name)
    print "using %s for gen_gf_surface" % (gen_gf_surface_location,)

    for map_type in gf_common.map_type_list:
        config = 'jessee_2017_%s.ini' % (map_type)
        
        model_dir = os.path.join(gf_common.sim_workflow_dir  , 'landslide_model')
        config_dir = os.path.join(gf_common.sim_workflow_dir  , 'config')
        ls_cmd = "python3 /usr/bin/gfail %s %s -d %s -c %s -o %s --set-bounds 'zoom, pgv, 0' --hdf5" % (config, gridfile, model_dir, config_dir, non_realisation_path)

        print 'Running landslide calculations'
        print ls_cmd
        subprocess.call(ls_cmd, shell=True)
        
        h5path = gf_common.find_h5(out_dir)
                
        xyz_path = create_xyz_name(out_dir, run_name, map_type)
        
        process_cmd = gen_gf_surface_location + " %s -t %s -o %s -type ls" % (h5path, run_name, xyz_path)
        
        if map_type == 'susceptibility':
            process_cmd += " -s" 

        print 'Running conversion'
        subprocess.call(process_cmd, shell=True)
        
        gf_common.plot(out_dir, xyz_path, run_name, "", map_type, "", 'landslide', path, realisation)


__main__()
