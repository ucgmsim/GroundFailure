'''
This has been tested for runs in v17p8 and several runs of v17p9

Produces a CCDF of the mean lines of all realisations for several runs

Requires: path to a run on Hypocentre which has realisations containing xyz data files

Usage: python All_runs_popn.py --datatype --grey --save --version --xAxis --run_file --runs
Example: python All_runs_popn.py 

Optional: 
-d, --datatype: Choose whether to use liquefaction or landslide data to plot the CCDF. Defaults to liquefaction
Example: --datatype landslide

-g, --grey: Add "--grey on" to plot all runs which are not specified with the --runs and --run_file arguments, in grey. By default non-specified
runs will not be plotted.
Example: --grey on

-s, --save: Use "--save here" to save the figure to the current working directory. Otherwise will save to an impact directory within /v17p8/ or /v17p9/
Example: --save here

-v, --version: Choose whether to plot runs from v17p8 or v17p9. Defaults to v17p8
Example: --version v17p9

-x, --xAxis: Choose whether to plot area (--xAxis area), population (--xAxis pop), or dwellings (--xAxis dwell) on the x-axis. Defaults to area
Example: --xAxis pop

-f, --run_file: Add a text file which has one run on each line. These runs will be plotted in colour.
Example: --run_file /home/fordw/Scripts/CCDF_scripts_and_plots/Run_test.txt

-r, --runs: List the runs that will be plotted in colour.
Example: --runs AlpineF2K AlpineK2T Hope1888

Writes a png of the CCDF to either the current working directory, or to /v17p9/Impact/ or /v17p8/Impact/

See USER group documentation 2018 for further information

@date 4/02/2018
@author Ford Wagner
@contact fwa33@canterbury.ac.nz
'''

import os
import argparse
from geopy import Point
from geopy import distance
import matplotlib.pyplot as plt
from matplotlib import gridspec
import numpy as np
import math

#Maximum number of runs that can be plotted in colour
MAX_COLOUR = 15

#Paths to the directories for the runs
P8_RUN_LIST = "/home/nesi00213/RunFolder/Cybershake/v17p8/Runs"
P9_RUN_LIST = "/home/nesi00213/RunFolder/Cybershake/v17p9/Runs"

#Where to save figures to
P8_SAVE_DIR = '/home/nesi00213/RunFolder/Cybershake/v17p8/Impact/'
P9_SAVE_DIR = '/home/nesi00213/RunFolder/Cybershake/v17p9/Impact/'

#Colours for plotting (same length as MAX_COLOUR)
COLOURS = ['#ff0000', '#00ff00', '#0000ff', '#ff00ff', '#ffff00', '#00ffff', '#000000', '#999999', '#ff6600', '#66ff00', '#66ff66', '#6666ff', '#ff66ff', '#66aaff', '#aaffaa']

LIQ_PATH = "/Impact/Liquefaction/"
LS_PATH = "/Impact/Landslide/"

#Zero point and y-axis limit
LIQ_ZERO = 0.00262
LIQ_LIM = 0.63

LS_ZERO = 0.005
LS_LIM = 0.345

#Models to use
LIQ_MODEL = '_zhu_2016_general_probability_nz-specific-vs30.xyz'
LS_MODEL = '_jessee_2017_probability.xyz'

#Area reference data
VSMALL_AREA = 290
VSMALL_REF = 'Wellington\nCity'
  
SMALL_AREA = 445
SMALL_REF = 'Nelson\nRegion'
  
MED_AREA = 1760
MED_REF = 'Stewart\nIsland'
  
LARGE_AREA = 4940
LARGE_REF = 'Auckland\nRegion'

LIQ_REF = 0.3
LS_REF = 0.16

#Databases to the population/dwelling pre-processed data
POP_DB = '/home/fordw/Scripts/CCDF_scripts_and_plots/popn_db.txt'
DWELL_DB = '/home/fordw/Scripts/CCDF_scripts_and_plots/dwelling_db.txt'


def getPopOrDwell(x_axis):
  '''
  Reads the population or dwelling database and returns the data in a dictionary.
  Dictionary key: latitude,longitude
  Dictionary value: meshblock area, meshblock population/dwellings
  '''
  data_dict = {}
  if x_axis == 'pop':
    database = POP_DB
  else:
    database = DWELL_DB
  with open(database) as data:
    for line in data:
      line = line.strip().split()
      lat, lng, area, pop = line[0], line[1], line[2], line[3]
      data_dict[(lat,lng)] = (area, pop)
  return data_dict
  
  
def getXyzData(xyz_file, zero_prob):
  '''
  Reads the xyz file and returns a list of lat/lng tuples, and a list of prob/lat/lng tuples.
  Only probabilities above the zero value are included.
  '''
  lat_lng = []
  data_list = []
  i = 0
  with open(xyz_file) as xyz:
    for line in xyz:
      if i < 6:
        i += 1
      else:
        line = line.strip().split()
        lng, lat, prob = line[0], line[1], float(line[2])
        lat_lng.append((lat,lng))
        if prob >= zero_prob and not math.isnan(prob):
          data_list.append((prob,lat,lng))
  return lat_lng, data_list
  
  
def getCellSize(lat_lng):
  '''
  Finds the upper left and upper right corners of a grid cell to get cell width then
  finds the the upper left and lower left corners of another cell to the cell height
  Returns the cell area in Sq.Km
  '''
  lat_lng.sort()
  corner1 = Point(lat_lng[0]) 
  corner2 = Point(lat_lng[1]) 
  lat_lng.sort(key=lambda a: (a[1], a[0]))
  corner3 = Point(lat_lng[0])
  corner4 = Point(lat_lng[1])

  cell_width = distance.great_circle(corner1,corner2).km
  cell_height = distance.great_circle(corner3,corner4).km
  
  return cell_width * cell_height


def makeAllRunsCCDF():
  #Processing arguments
  parser = argparse.ArgumentParser()
  parser.add_argument('-f', '--run_file', help = 'Add a path to a text file (with one run on each line) of the runs which need to be plotted')
  parser.add_argument('-r', '--runs', nargs = '+', help = 'Add the names of the specific runs to plot')
  parser.add_argument('-g', '--grey', default = 'off', help = 'Add "--grey on" to plot the non-specified runs from v17p8/p9 in grey. By default these runs will not be plotted')
  parser.add_argument('-d', '--datatype', default = 'liq', help = 'Choose whether to plot liquefaction(liq) or landslide(ls) data. Defaults to liquefaction')
  parser.add_argument('-v', '--version', default = 'v17p8', help = 'Specify whether to use v17p8 ("-v v17p8") or v17p9 ("-v v17p9") data. Defaults to v17p8')
  parser.add_argument('-s', '--save', default = 'Impact', help = 'Add "--save here" argument to save the CCDF to the current working directory. By default it saves to an impact folder within .../v17p8/ or .../v17p9/')
  parser.add_argument('-x', '--xAxis', default = 'area', help = 'Choose whether to plot area ("-x area"), population ("-x pop"), or dwellings ("-x dwell") data on the x-axis')
  args = parser.parse_args()
  
  if args.datatype == 'liq' or args.datatype == 'liquefaction':
    zero_prob = LIQ_ZERO
    model = LIQ_MODEL
    y_lim = LIQ_LIM
    path_type = LIQ_PATH
    ref_point = LIQ_REF
    is_liq = True
  elif args.datatype == 'ls' or args.datatype == 'landslide':
    zero_prob = LS_ZERO
    model = LS_MODEL
    y_lim = LS_LIM
    path_type = LS_PATH
    ref_point = LS_REF
    is_liq = False
  else:
    print '\n"--datatype ' + args.datatype + '" not recognised. Please use "--datatype liq" argument to specify liquefaction (liq), or "--datatype ls" to specify landslide (ls) data\n'
    quit()
  
  if args.version == 'v17p8':
    run_path = P8_RUN_LIST
    save_dir = P8_SAVE_DIR
  elif args.version == 'v17p9':
    run_path = P9_RUN_LIST
    save_dir = P9_SAVE_DIR
  else:
    print '\n"--version ' + args.version +'" not recognised. Please use "--version v17p8" to specify v17p8, or "--version v17p9" to specify v17p9\n'
    quit()
  
  if args.save == 'here':
    save_dir = os.getcwd() + '/'
  elif args.save != 'Impact':
    print '\n"--save ' + args.save + '" not recognised. Please use "--save here" to save to the current working directory, or "--save impact" to save to ' + save_dir + '\n'
    quit()
    
  print '\nFigure will save to:\n' + save_dir + '\n'
  if not os.path.isdir(save_dir):
    print save_dir + ' is not a directory. \nPlease create this directory or add "--save here" when calling the script to save to the current working directory'
    quit()
  
  #Fills a list with all of the runs in v17p8 or v17p9. "csv_33" was causing issues when testing
  unfiltered_run_list = os.listdir(run_path)
  full_run_list = []
  for run in unfiltered_run_list:
    if not os.path.isfile(run_path + "/" + run)and run != 'csv_33':
      full_run_list.append(run)
  
  #Fills a list with all of the runs that need to be plotted
  all_runs = False
  run_list = []
  if args.run_file is None:
    if args.runs is None:
      run_list = full_run_list
      all_runs = True
    else:
      run_list = args.runs
  else:
    try:
      with open(args.run_file) as run_file:
        for line in run_file:
          run_list.append(line.strip())
      if args.runs is not None:
        for run in args.runs:
          if run not in run_list:
            run_list.append(run)
    except IOError:
      print args.run_file + ' is not a file.\nPlease check the file path and run the script again\n'
      quit()
  
  #Fills lists with runs which will be plotted in grey, and runs which will be plotted in colour
  grey_plot = []
  colour_plot = []
  grey = False
  if args.grey == 'on':
    grey = True
    if not all_runs:
      colour_plot = run_list
    grey_plot = [x for x in full_run_list if x not in colour_plot]
  elif args.grey != 'off':
    print '"--grey ' + args.grey + '" not recognised. To plot non-specified runs in grey please add "--grey on" argument when calling the script\n'
    quit()
  else:
    colour_plot = run_list
  
  is_area = False
  is_pop = False
  if args.xAxis == 'area':
    is_area = True
    x_label = ' Impacted Area (Sq.Km)'
  elif args.xAxis == 'pop':
    print 'Cannot calculate a mean line for population data. Plotting the first realisation for each run instead'
    x_label = ' Impacted Population'
    data_dict = getPopOrDwell('pop')
    title_type = '(Population)'
    is_pop = True
  elif args.xAxis == 'dwell':
    print 'Cannot calculate a mean line for dwelling data. Plotting the first realisation for each run instead'
    x_label = ' Impacted Dwellings'
    data_dict = getPopOrDwell('dwell')
    title_type = '(Dwellings)'
  else:
    print '"--xAxis ' + args.xAxis + '" not recognised \nPlease use "--xAxis area", "--xAxis pop", or "--xAxis dwell" to choose to plot area, population, or dwellings on the x-axis\n'
    quit()
  
  #If too many runss are being plotted in colour a message appears explaining that all runs will be plotted in grey
  num_colour_runs = len(colour_plot)
  if num_colour_runs > MAX_COLOUR:
    print 'Too many runs to plot in colour. Please choose fewer runs to plot in colour\nDefaulting to plotting the specified lines in grey\n'
    grey_plot = colour_plot
    colour_plot = []
    num_colour_runs = 0
    too_many_runs = True
  else:
    too_many_runs = False
  
  fig = plt.figure()
  gs = gridspec.GridSpec(1,1)
  ax = fig.add_subplot(gs[0,0])
  
  #Orders all of the runs to plot
  to_plot = colour_plot + grey_plot
  to_plot = list(set(to_plot))
  to_plot.sort()
  
  col_index = 0
  max_x = 0
  
  for run in to_plot:
    #Stores data from each run
    prob_dict = {}
    x_list = []
    realisation_list = []
    
    first_realisation = True
    lat_lng = []
    
    #If a run does not exist then this will end the script
    try:
      realisation_list = os.listdir(run_path + '/' + run + path_type)
      if 'CCDF' in realisation_list:
        realisation_list.remove('CCDF')
    except OSError:
      print 'Cannot find path to run: ' + run + '\nPlease modify the runs to plot by using the --runs or --run_file arguments\n'
      quit()
      
    realisation_list.sort()
    
    #Cannot calculate the mean of population/dwelling data and so only the first realisation is plotted for each run
    if not is_area:
      realisation_list = [realisation_list[0]]
    
    for realisation in realisation_list:
      prob_dict[realisation] = []
      xyz_path = run_path + '/' + run + path_type + realisation + '/' + run + model
      lat_lng, prob_dict[realisation] = getXyzData(xyz_path, zero_prob)
    
    cell_area = getCellSize(lat_lng)
    cumulat_x = 0
    average_prob = []
    
    #Calculates the mean of all realisations for a run
    if is_area:
      longest_prob = 0
      for realisation in prob_dict:
        prob_dict[realisation] = [x[0] for x in prob_dict[realisation]]
        prob_dict[realisation].sort(reverse = True)
        if len(prob_dict[realisation]) > longest_prob:
          longest_prob = len(prob_dict[realisation])
      
      for realisation in prob_dict:
        while len(prob_dict[realisation]) != longest_prob:
          prob_dict[realisation].append(0)
      
      for i in range(longest_prob):
        cumulat_x += cell_area
        x_list.append(cumulat_x)
        
        average = []
        for realisation in prob_dict:
          average.append(prob_dict[realisation][i])
        mean = np.mean(average)
        average_prob.append(mean)
    
    #If data is population or dwelling, then finds data for the first realisation
    else:
      prob_dict[realisation_list[0]].sort(reverse = True)
      for data in prob_dict[realisation_list[0]]:
        prob,lat,lng = data[0],data[1],data[2]
        PorD_data = data_dict.get((lat,lng))
        if PorD_data == None:
          continue
        else:
          area, pop_or_dwell = PorD_data[0], PorD_data[1]
          try:
            scaled_area = cell_area/float(area)
          except ZeroDivisionError:
            scaled_area = 0
          if scaled_area > 1:
              scaled_area = 1
          try:
            scaled_PorD = scaled_area * float(pop_or_dwell)
          except ValueError:
            scaled_PorD = 0
        cumulat_x += scaled_PorD
        
        x_list.append(cumulat_x)
        average_prob.append(prob)
      
    average_prob.insert(0,average_prob[0])
    x_list.insert(0,0)
    
    #Tracks run with largest impacted area/pop/dwellings
    if cumulat_x > max_x:
      max_x = cumulat_x
    
    #Plots runs in the correct colour
    if run in colour_plot:
      if all_runs:
        ax.plot(x_list, average_prob, color = COLOURS[col_index], label = run, zorder = 2)
      else:
        ax.plot(x_list, average_prob, color = COLOURS[col_index], label = run, linewidth = 2, zorder = 1)
      col_index += 1
    elif run in grey_plot:
      ax.plot(x_list, average_prob, color = 'grey')
    print run +' done...'
  
  #Title and labels for the CCDF
  if is_area:
    if is_liq:
      if all_runs:
        ax.set_title('Mean Liquefaction CCDF (Area) for All Runs')
      elif grey:
        ax.set_title('Mean Liquefaction CCDF (Area) for All Runs \n (Specified Runs in Colour)')
      else:
        ax.set_title('Mean Liquefaction CCDF (Area) for Specified Runs')
      ax.set_ylabel('Liquefaction Areal Percentage')
    else:
      if all_runs:
        ax.set_title('Mean Landslide CCDF (Area) for All Runs')
      elif grey:
        ax.set_title('Mean Landslide CCDF (Area) for All Runs \n (Specified Runs in Colour)')
      else:
        ax.set_title('Mean Landslide CCDF (Area) for Specified Runs')
      ax.set_ylabel('Landslide Areal Percentage')
  else:
    if is_liq:
      if all_runs:
        ax.set_title('Liquefaction CCDF ' + title_type + ' \nfor one realisation of All Runs')
      elif grey:
        ax.set_title('Liquefaction CCDF ' + title_type + ' for one realisation of All Runs \n (Specified Runs in Colour)')
      else:
        ax.set_title('Liquefaction CCDF ' + title_type + ' for \none realisation of Specified Runs')
      ax.set_ylabel('Liquefaction Areal Percentage')
    else:
      if all_runs:
        ax.set_title('Landslide CCDF ' + title_type + ' for one realisation of All Runs')
      elif grey:
        ax.set_title('Landslide CCDF ' + title_type + ' for one realisation of All Runs \n (Specified Runs in Colour)')
      else:
        ax.set_title('Landslide CCDF ' + title_type + ' for \none realisation of Specified Runs')
      ax.set_ylabel('Landslide Areal Percentage')
  
  #Formatting the CCDF
  ax.set_xlabel(x_label)
  ax.set_xscale('log')
  ax.set_xlim((1, max_x))
  ax.set_ylim((0,y_lim))
  ax.xaxis.set_ticks_position('none')
  ax.yaxis.set_ticks_position('left')
  ax.spines['right'].set_visible(False)
  ax.spines['top'].set_visible(False)
  
  #Adding a legend
  if num_colour_runs > 0:
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.7, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
  
  #Adds a reference line when plotting only grey lines against area 
  if is_area and len(colour_plot) == 0:
    if max_x > 8500:
      ax.axvline(x=LARGE_AREA, linestyle = '--')
      ax.text(LARGE_AREA, ref_point, 'Area of the\n' + LARGE_REF + '\n (' + str(LARGE_AREA) + ' Sq.Km)', multialignment = 'center')
      ref_used = LARGE_AREA
    elif max_x > 3750:
      ax.axvline(x=MED_AREA, linestyle = '--')
      ax.text(MED_AREA, ref_point, 'Area of\n' + MED_REF + '\n (' + str(MED_AREA) + ' Sq.Km)', multialignment = 'center')
      ref_used = MED_AREA
    elif max_x > 850:
      ax.axvline(x=SMALL_AREA, linestyle = '--')
      ax.text(SMALL_AREA, ref_point, 'Area of the\n' + SMALL_REF + '\n (' + str(SMALL_AREA) + ' Sq.Km)', multialignment = 'center')
      ref_used = SMALL_AREA
    else: 
      ax.axvline(x=VSMALL_AREA, linestyle = '--')
      ax.text(VSMALL_AREA, ref_point, 'Area of\n' + VSMALL_REF + '\n (' + str(VSMALL_AREA) + ' Sq.Km)', multialignment = 'center')
      ref_used = VSMALL_AREA
  
  #Determining the filename
  colour_plot = list(set(colour_plot))
  colour_plot.sort()
  specific_runs = '_'.join(colour_plot)
  if all_runs and grey:
    if is_liq:
      if is_area:
        filename = 'Liq_CCDF_Area_All_Runs_Grey'
      elif is_pop:
        filename = 'Liq_CCDF_Population_All_Runs_Grey'
      else:
        filename = 'Liq_CCDF_Dwellings_All_Runs_Grey'
    else:
      if is_area:
        filename = 'Ls_CCDF_Area_All_Runs_Grey'
      elif is_pop:
        filename = 'Ls_CCDF_Population_All_Runs_Grey'
      else:
        filename = 'Ls_CCDF_Dwellings_All_Runs_Grey'
  elif all_runs:
    if is_liq:
      if is_area:
        filename = 'Liq_CCDF_Area_All_Runs_Colour'
      elif is_pop:
        filename = 'Liq_CCDF_Population_All_Runs_Colour'
      else:
        filename = 'Liq_CCDF_Dwellings_All_Runs_Colour'
    else: 
      if is_area:
        filename = 'Ls_CCDF_Area_All_Runs_Colour'
      elif is_pop:
        filename = 'Ls_CCDF_Population_All_Runs_Colour'
      else:
        filename = 'Ls_CCDF_Dwellings_All_Runs_Colour'
  elif grey:
    if is_liq:
      if is_area:
        filename = 'Liq_CCDF_Area_All_Runs_Grey_Except_' + specific_runs
      elif is_pop:
        filename = 'Liq_CCDF_Population_All_Runs_Grey_Except_' + specific_runs
      else:
        filename = 'Liq_CCDF_Dwellings_All_Runs_Grey_Except_' + specific_runs
    else:
      if is_area:
        filename = 'Ls_CCDF_Area_All_Runs_Grey_Except_' + specific_runs
      elif is_pop:
        filename = 'Ls_CCDF_Population_All_Runs_Grey_Except_' + specific_runs
      else:
        filename = 'Ls_CCDF_Dwellings_All_Runs_Grey_Except_' + specific_runs
  elif too_many_runs:
    grey_plot = list(set(grey_plot))
    grey_plot.sort()
    specific_runs = '_'.join(grey_plot)
    if is_liq:
      if is_area:
        filename = 'Liq_CCDF_Area_Specific_Runs_Grey_' + specific_runs
      elif is_pop:
        filename = 'Liq_CCDF_Population_Specific_Runs_Grey_' + specific_runs
      else:
        filename = 'Liq_CCDF_Dwellings_Specific_Runs_Grey_' + specific_runs
    else:
      if is_area:
        filename = 'Ls_CCDF_Area_Specific_Runs_Grey_' + specific_runs
      elif is_pop:
        filename = 'Liq_CCDF_Population_Specific_Runs_Grey_' + specific_runs
      else:
        filename = 'Liq_CCDF_Dwellings_Specific_Runs_Grey_' + specific_runs
  else:
    if is_liq:
      if is_area:
        filename = 'Liq_CCDF_Area_Specified_Runs_' + specific_runs
      elif is_pop:
        filename = 'Liq_CCDF_Population_Specified_Runs_' + specific_runs
      else:
        filename = 'Liq_CCDF_Dwellings_Specified_Runs_' + specific_runs
    else:  
      if is_area:
        filename = 'Ls_CCDF_Area_Specified_Runs_' + specific_runs
      elif is_pop:
        filename = 'Ls_CCDF_Population_Specified_Runs_' + specific_runs
      else:
        filename = 'Ls_CCDF_Dwellings_Specified_Runs_' + specific_runs
  
  #Saving the figure. Limits the length of the file name
  saving = save_dir + filename
  if len(saving) > 160:
    saving = saving[:150] + '_etc'
  fig.savefig(saving)
  fig.savefig('All_runs_test')
  print('\nSaving as:\n' + saving + '.png\n')
  
  print 'Maximum' + x_label + ': ' + str(max_x) + '\nDone\n'
  
if __name__ == '__main__':
  makeAllRunsCCDF()