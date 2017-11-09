"""
Common shared functions used by both plot_liq and plot_ls

@date 6 Oct 2017
@author Jason Motha
@contact jason.motha@canterbury.ac.nz
"""

import glob
import os
import argparse
from contextlib import contextmanager
import subprocess

sim_workflow_dir = "/home/nesi00213/groundFailure"

@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)

def get_path_name():
    parser = argparse.ArgumentParser(description='Run the various steps required to plot liquefaction for a given quake')
    parser.add_argument('path', help='path to folder that contains quake info (usually in realtime)')

    args = parser.parse_args()

    path = args.path

    return path, get_run_name(path)
    

def get_run_name(path):
    if path[-1] == '/':
        path = path[:-1]
    return os.path.basename(path)

def check_gridfile(gridfile):
    if len(gridfile) > 0 and os.path.exists(gridfile[0]):
        print "Gridfile found at: %s" % gridfile
        return True
    else:
        print "gridfile not found at: %s" % gridfile
        return False

def find_gridfile(path):
    gridfile = glob.glob(os.path.join(path, 'GM/Sim/*/PNG_tssum/grid.xml'))

    if not check_gridfile(gridfile):
        gridfile = glob.glob(os.path.join(path, 'GM/Sim/*/*/PNG_tssum/grid.xml'))
        if not check_gridfile(gridfile):
            exit()

    gridfile = gridfile[0]

def plot(out_dir, xyz_path, run_name, vs30_model, map_type, model, gf_type):
    
    with cd(out_dir):
        print 'Plotting'
        plot_cmd = "plot_stations.py %s" % xyz_path
        print plot_cmd
        subprocess.call(plot_cmd, shell=True)

    plot_file = os.path.join(out_dir, "PNG_stations/c000.png")
    plot_name = os.path.join(out_dir, "%s_%s_%s_%s_%s.png" % (run_name, gf_type, vs30_model, map_type, model))

    if not os.path.exists(plot_file):
        print "output plot not found at: %s" % plot_file
        exit()

    os.rename(plot_file, plot_name)
    
    print "%s was created" % plot_name 
