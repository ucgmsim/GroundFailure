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

plot_stations_path = 'plot_stations.py'
gen_gf_surface_name = 'gen_gf_surface.py'
sim_workflow_dir = "/home/nesi00213/groundfailure" #only used if files cannot be found

model_list = ('general', 'coastal')
map_type_list = ('probability', 'susceptibility')
vs30_model_list = ('nz-specific-vs30', 'topo-based-vs30')


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
    parser.add_argument('-r', '--realisation', help='If the run folder has multiple realisations; selects the correct one')

    args = parser.parse_args()

    path = args.path
    realisation = args.realisation

    return path, get_run_name(path), realisation
    

def get_run_name(path):
    if path[-1] == '/':
        path = path[:-1]
    return os.path.basename(path)


def check_file_exists(file, filetype):
    if len(file) > 0 and os.path.exists(file[0]):
        print "%s found at: %s" % (filetype, file)
        return True
    else:
        print "%s not found at: %s" % (filetype, file)
        return False


def create_output_path(path, gf_type, realisation=None):
    if realisation is None:
        realisation = ''
    return os.path.join(path, 'Impact/', gf_type, realisation)


def find_gridfile(path, realisation=None):
    if realisation is not None:
        loc = os.path.join(path, 'GM/Sim/Data/*', realisation, 'grid.xml')
        gridfile = glob.glob(loc)
    else:
        gridfile = glob.glob(os.path.join(path, 'GM/Sim/*/PNG_tssum/grid.xml'))
        if not check_file_exists(gridfile, 'gridfile'):
            gridfile = glob.glob(os.path.join(path, 'GM/Sim/*/*/PNG_tssum/grid.xml'))

    if not check_file_exists(gridfile, 'gridfile'):
        exit()

    gridfile = gridfile[0]
    return gridfile

def find_h5(path):
	h5path = os.path.join(path, '*.hdf5')
	print h5path
	h5file = glob.glob(h5path)

	if not check_file_exists(h5file ,'h5 file'):
		h5path = os.path.join(path, '*/*.hdf5')
		print h5path
		h5file = glob.glob(h5path)
		
	if not check_file_exists(h5file ,'h5 file'):
		exit()
       
	h5file = h5file[0]
	return h5file
	
def get_srf_path(base_dir, realisation=None):
    srf_file = []
    if realisation is None:
        srf_file.extend(glob.glob('%s/Src/Model/*/Srf/*.srf' % (base_dir)))
        srf_file.extend(glob.glob('%s/Src/Model/*/*/Srf/*.srf' % (base_dir)))
    else:
        srf_file.extend(glob.glob('%s/Src/Model/*/Srf/%s.srf' % (base_dir, realisation)))
    if len (srf_file) > 0:
        return srf_file[0]
    else:
        return None

def plot(out_dir, xyz_path, run_name, vs30_model, map_type, model, gf_type, path=None, realisation=None):
    
    with cd(out_dir):
        print 'Plotting'
        plot_cmd = "%s \"%s\"" % (plot_stations_path, xyz_path)
        if map_type == 'probability':
            srf_path = get_srf_path(path, realisation)
            if srf_path is not None:
                plot_cmd += ' --srf %s' % (srf_path,)
            else:
                print "srf file not found; not overlaying fault"
        print plot_cmd
        subprocess.call(plot_cmd, shell=True)

    plot_file = os.path.join(out_dir, "PNG_stations/c000.png")
    plot_name = os.path.join(out_dir, "%s_%s_%s_%s_%s.png" % (run_name, gf_type, vs30_model, map_type, model))

    if not os.path.exists(plot_file):
        print "output plot not found at: %s" % plot_file
        exit()

    os.rename(plot_file, plot_name)
    
    print "%s was created" % plot_name 
