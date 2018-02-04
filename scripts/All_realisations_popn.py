'''
This has been tested for runs in v17p8 and several runs of v17p9

Produces a CCDF showing scope of liquefaction/landsliding for each realisation for a run

Requires: path to a run on Hypocentre which has realisations containing xyz data files

Usage: python All_realisations_popn.py /path/to/run/ --datatype --mean --regions --save --xAxis
Example: python All_realisations_popn.py /home/nesi00213/RunFolder/Cybershake/v17p9/Runs/AlpineF2K

Optional: 
-d, --datatype: Choose whether to use liquefaction or landslide data to plot the CCDF. Defaults to liquefaction
Example: --datatype landslide

-m, --mean: Add --mean on to make all lines grey and to include a mean line of all realisations in black. Default is off
Example: --mean on

-s, --save: Use "--save here" to save the figure to the current working directory. Otherwise will save to a CCDF directory within the realisation
Example: --save here

-x, --xAxis: Choose whether to plot area (--xAxis area), population (--xAxis pop), or dwellings (--xAxis dwell) on the x-axis. Defaults to area
Example: --xAxis pop

-r, --regions: Choose whether to remove region subplots (--regions off) or to include them (--regions on). Defaults to regions being on.
Example: --regions off

Writes a png of the CCDF to either the current working directory, or to a CCDF directory within run/Impact/Liq or landslide/

See USER group documentation 2018 for further information

@date 4/02/2018
@author Ford Wagner
@contact fwa33@canterbury.ac.nz
'''

import argparse
import math
import os
from geopy import Point
from geopy import distance
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.font_manager import FontProperties
import numpy as np
import glob
import urllib

#Setting zero probability cut-offs and y-axis limits
LIQ_ZERO = 0.00262
LIQ_LIM = 0.65

LS_ZERO = 0.005
LS_LIM = 0.345

#Path between the run folder and the realisation folders
LIQ_PATH = '/Impact/Liquefaction/'
LS_PATH = '/Impact/Landslide/'

#Model being plotted
LIQ_MODEL = '_zhu_2016_general_probability_nz-specific-vs30.xyz'
LS_MODEL = '_jessee_2017_probability.xyz'

#Reference data
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

#Text files of pre-processed data
REGION_DB = '/home/fordw/GroundFailure/scripts/Region_database.txt'
POP_DB = '/home/fordw/Scripts/CCDF_scripts_and_plots/popn_db.txt'
DWELL_DB = '/home/fordw/Scripts/CCDF_scripts_and_plots/dwelling_db.txt'

#colours for plotting each realisation
COLOURS = ['#ff0000', '#ff9900', '#ffff00', '#00ff00', '#0000ff', '#ff00ff']


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
  
  
def getRegionData():
  '''
  Reads a text file of lat, lng, region data and returns the data as a dictionary.
  Dictionary keys: latitude, longitude tuples
  Dictionary values: region at that lat/lng
  '''
  region_dict = {}
  with open(REGION_DB) as region_data:
    for line in region_data:
      line = line.split()
      lat, lng = line[0], line[1]
      region = ' '.join(line[2:])
      region_dict[(lat,lng)] = region
  return region_dict
  
  
def getRegionList(region_dict, data_list):
  '''
  Returns a list of all the impacted regions
  '''
  region_list = []
  for data in data_list:
    lat, lng = data[1], data[2]
    region = region_dict.get((lat,lng))
    if region not in region_list:
      region_list.append(region)
  return region_list
  
  
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
  
  
def updateRegionData(region_dict, data_list):
  '''
  Checks through the data list and if any data is not in the region dictionary then it is added.
  Returns an updated dictionary of lat/lng : region data
  '''
  key = 'd5077171350641bdb83afe4c97f3daf6'
  api_url = 'https://koordinates.com/services/query/v1/vector.json?'
  
  updating = False
  with open(REGION_DB, 'a') as region_data:
    for data in data_list:
      prob, lat, lng = data[0], data[1], data[2]
      if (lat,lng) not in region_dict:
        if not updating:
          print 'Updating the database. This may take awhile...\n'
          updating = True
        print prob
        
        url = api_url + 'key=' + key + '&layer=4240&x=' + lng + '&y=' + lat
        urllib.urlretrieve(url, "New_region_data")
        
        with open("New_region_data") as new_data:
          for line in new_data:
            line = line.split(',')
            region = line[-2][10:-2]
        region_data.write(lat + ' ' + lng + ' ' + region + '\n')
        region_dict[(lat,lng)] = region
        print(region)
  if updating:
    print 'Updated the database!\n'
  return region_dict
  

def makeAllRealisationsCCDF():
  #Processing arguments
  parser = argparse.ArgumentParser()
  parser.add_argument('run_path', help = 'File path to the run to be plotted e.g. /home/nesi00213/RunFolder/Cybershake/v17p9/Runs/AlpineF2K')
  parser.add_argument('-d', '--datatype', default = 'liq', help = 'Choose whether to plot liquefaction(liq) or landslide(ls) data. Defaults to liquefaction')
  parser.add_argument('-m', '--mean', default = 'off', help = 'Choose to plot the data in grey with a black mean line ("--mean on") or to plot in colour with no mean line ("--mean off")')
  parser.add_argument('-r', '--regions', default = 'on', help = 'Choose whether to include subplots for the impacted regions ("-r on") or not ("-r off")')
  parser.add_argument('-s', '--save', default = 'CCDF', help = 'Add "--save here" argument to save the CCDF to the current working directory. By default it saves to a CCDF directory within the folder that the realisations are saved.')
  parser.add_argument('-x', '--xAxis', default = 'area', help = 'Choose whether to plot area ("-x area"), population ("-x pop"), or dwellings ("-x dwell") data on the x-axis.')
  args = parser.parse_args()
  
  #Setting variables based on given arguments. Gives error messages if any problems
  if args.mean == 'on':
    mean = True
  else:
    if args.mean != 'off':
      print('\n"--mean ' + args.mean + '" not recognised\nTo have grey lines with a black mean line, add "--mean on" when calling this script\n')
      quit()
    colours = COLOURS
    mean = False
    
  regions = True
  if args.regions == 'off':
    regions = False
  elif args.regions != 'on':
    print '\n"--regions ' + args.regions + '" not recognised' 
    print 'Please call the script with "--regions on" to include region subplots or with "--regions off" to remove region subplots\n'
    quit()
    
  if args.datatype == 'liq' or args.datatype == 'liquefaction':
    is_liq = True
    zero_prob = LIQ_ZERO
    y_lim = LIQ_LIM
    ref_point = LIQ_REF
    model = LIQ_MODEL
    path_type = LIQ_PATH
  elif args.datatype == 'ls' or args.datatype == 'landslide':
    is_liq = False
    zero_prob = LS_ZERO
    y_lim = LS_LIM
    ref_point = LS_REF
    model = LS_MODEL
    path_type = LS_PATH
  else:
    print '\n"--datatype "' + args.datatype + '" not recognised. \nPlease add "--datatype liquefaction" or "--datatype landslide" in argument to specify datatype.\n'
    quit()
    
  if args.save == 'here':
    save_dir = os.getcwd() + '/'
  elif args.save == 'CCDF':
    save_dir = args.run_path + path_type + 'CCDF/'
  else:
    print '\n"--save ' + args.save + '" not recognised\nTo save to the current working directory add "--save here" or leave to save to a CCDF directory\n'
    quit()
    
  print '\nFigure will save to:\n' + save_dir + '\n'
  if not os.path.isdir(save_dir):
    print save_dir + ' is not a directory. \nPlease create this directory or add "--save here" when calling the script to save to the current working directory'
    quit()
  
  #Fills pop/dwellings dictionary if required
  is_area = False
  is_pop = False
  if args.xAxis == 'area':
    is_area = True
    x_label = ' Impacted Area (Sq.Km)'
  elif args.xAxis == 'pop':
    if mean:
      print 'Cannot calculate a mean line for population data. Plotting all lines in grey without a mean line...\n'
    x_label = ' Impacted Population'
    data_dict = getPopOrDwell('pop')
    is_pop = True
  elif args.xAxis == 'dwell':
    if mean:
      print 'Cannot calculate a mean line for dwelling data. Plotting all lines in grey without a mean line...\n'
    x_label = ' Impacted Dwellings'
    data_dict = getPopOrDwell('dwell')
  else:
    print '"--xAxis ' + args.xAxis + '" not recognised \nPlease use "--xAxis area", "--xAxis pop", or "--xAxis dwell" to choose to plot area or population on the x-axis\n'
    quit()
  
  #Finding filename
  if mean:
    if regions:
      if is_area:
        file_name = "Mean_All_Realisations_Region_CCDF_Area"
      elif is_pop:
        file_name = "Mean_All_Realisations_Region_CCDF_Population"
      else:
        file_name = "Mean_All_Realisations_Region_CCDF_Dwellings"
    else:
      if is_area:
        file_name = "Mean_All_Realisations_CCDF_Area"
      elif is_pop:
        file_name = "Mean_All_Realisations_CCDF_Population"
      else:
        file_name = "Mean_All_Realisations_CCDF_Dwellings"
  else:
    if regions:
      if is_area:
        file_name = "All_Realisations_Region_CCDF_Area"
      elif is_pop:
        file_name = "All_Realisations_Region_CCDF_Population"
      else:
        file_name = "All_Realisations_Region_CCDF_Dwellings"
    else:
      if is_area:
        file_name = "All_Realisations_CCDF_Area"
      elif is_pop:
        file_name = "All_Realisations_CCDF_Population"
      else:
        file_name = "All_Realisations_CCDF_Dwellings"
  
  #Checking if the run name is too long to fit on the figure
  run_path = args.run_path.split('/')
  run = run_path[-1]
  if len(run) > 9:
    too_long = True
  else:
    too_long = False
  
  #Getting CCDF title
  model_details = model.split('_')
  if is_liq:
    model_name = model_details[3] + ' probability, '
    if too_long:
      map_type = model_details[-1][0:-9]
    else:
      map_type = model_details[-1][0:-4]
    model_full = model_name + map_type
  else:
    model_full = 'Landslide probability ' + model_details[2]
  if mean:
    ccdf_title = 'Mean CCDF for all realisations of ' + run + '\n(' + model_full + ')'
  else:
    ccdf_title = 'CCDF for all realisations of ' + run + ' (' + model_full + ')\n'
  
  realisation_list = os.listdir(args.run_path + path_type)
  if 'CCDF' in realisation_list:
    realisation_list.remove('CCDF')
  realisation_list.sort()
    
  num_realisations = len(realisation_list)
  if num_realisations > 6:
    print 'Too many realisations to plot in colour. Defaulting to grey lines with a black mean line\n'
    mean = True
  
  #Data structures for storing plotting data
  prob_dict = {}  
  x_dict = {}
  
  if regions:
    region_probs = {}
    region_x = {}
    region_dict = getRegionData()
  
  fig = plt.figure()
  gs = gridspec.GridSpec(2,2)
  
  #Tracks colour to plot in, first iteration of the following loop, and max x-axis value across the realisations
  first_realisation = True
  col_index = 0
  max_x = 0
  
  for realisation in realisation_list:
    prob_dict[realisation] = []
    x_dict[realisation] = []
    
    #Finds the xyz file for the specific model within each realisation
    all_files = glob.glob(args.run_path + path_type + realisation + '/*')
    xyz_path = None
    for f in all_files:
      if model in f:
        xyz_path = f
    if xyz_path is None:
      print 'Cannot find xyz file for the model (' + model + '( in:\n' + args.run_path + path_type + realisation + '/\n'
      quit()
    
    lat_lng, data_list = getXyzData(xyz_path, zero_prob)
    
    #Assumes cell area doesn't change between realisations so only calculates once
    if first_realisation:
      cell_area = getCellSize(lat_lng)
      
    if regions:
        region_dict = updateRegionData(region_dict, data_list)
        region_list = getRegionList(region_dict, data_list)

        region_probs[realisation] = {}
        region_x[realisation] = {}
        
        for region in region_list:
          region_probs[realisation][region] = []
          region_x[realisation][region] = []

    data_list.sort(reverse = True)
    cumulat_x = 0
    
    #Adds data to relevant lists
    for data in data_list:
      prob,lat,lng = data[0],data[1],data[2]
      if is_area:
        cumulat_x += cell_area
      else:
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
      prob_dict[realisation].append(prob)
      x_dict[realisation].append(cumulat_x)
      
      if regions:
        region = region_dict.get((lat,lng))
        if is_area:
          tup = (prob, cell_area)
          region_probs[realisation][region].append(tup)
        else:
          region_probs[realisation][region].append((prob, scaled_PorD))
    
    #Adding zero points
    prob_dict[realisation].insert(0, prob_dict[realisation][0])
    x_dict[realisation].insert(0,0)
    
    if cumulat_x > max_x:
      max_x = cumulat_x
    
    #Filling x-axis list for the regions
    if regions:
      for region in region_list:
        cumulat_x = 0
        if len(region_probs[realisation][region]) != 0:
          for data in region_probs[realisation][region]:
            cumulat_x += data[1]
            region_x[realisation][region].append(cumulat_x)
          region_probs[realisation][region].insert(0, region_probs[realisation][region][0])
          region_x[realisation][region].insert(0,0)
      for region in region_list:
        region_probs[realisation][region] = [x[0] for x in region_probs[realisation][region]]
    else:
      region_list = ['None']
      
    if len(region_list) == 1 and first_realisation:
      ax1 = fig.add_subplot(gs[:,:])
      multiple = False
    
    #Finding two most damaged regions to plot
    elif first_realisation:
      regions_damaged = []
      for region in region_list:
        if len(region_x[realisation][region]) != 0:
          regions_damaged.append((region_x[realisation][region][-1], region))
      regions_damaged.sort()
      regions_to_plot = [regions_damaged[-1][1], regions_damaged[-2][1]]
    
      ax1 = fig.add_subplot(gs[0,:])
      ax2 = fig.add_subplot(gs[1,0])
      ax3 = fig.add_subplot(gs[1,1])
      multiple = True
      
    if mean:
      ax1.plot(x_dict[realisation], prob_dict[realisation], color = 'grey', label = realisation, zorder = 1)
    else:
      ax1.plot(x_dict[realisation], prob_dict[realisation], color = colours[col_index], label = realisation, zorder = 1)
      
    if multiple:
      if mean:
        ax2.plot(region_x[realisation][regions_to_plot[0]], region_probs[realisation][regions_to_plot[0]], color = 'grey', zorder = 1)
      else:
        ax2.plot(region_x[realisation][regions_to_plot[0]], region_probs[realisation][regions_to_plot[0]], color = colours[col_index], zorder = 1)
    
      if len(region_list) > 1:
        if mean:
          ax3.plot(region_x[realisation][regions_to_plot[1]], region_probs[realisation][regions_to_plot[1]], color = 'grey', zorder = 1)
        else:
          ax3.plot(region_x[realisation][regions_to_plot[1]], region_probs[realisation][regions_to_plot[1]], color = colours[col_index], zorder = 1)
    
    col_index += 1
    first_realisation = False
  
  #Calculating a mean line of all realisations
  if mean and is_area:
    average_prob = []
    upper = []
    lower = []
    area_list = []
    
    longest_prob = 0
    for realisation in prob_dict:
      if len(prob_dict[realisation]) > longest_prob:
        longest_prob = len(prob_dict[realisation])
    
    for realisation in prob_dict:
      while len(prob_dict[realisation]) != longest_prob:
        prob_dict[realisation].append(0)
    
    cumulat_area = 0
    
    for i in range(longest_prob):
      average = []
      std_dev = []
      
      for realisation in prob_dict:
        average.append(prob_dict[realisation][i])
      avg = np.mean(average)
      std_dev = np.std(average,ddof = 1)
      
      average_prob.append(avg)
      upper.append(avg + std_dev)
      lower.append(avg - std_dev)
      
      area_list.append(cumulat_area)
      cumulat_area += cell_area
    
    ax1.plot(area_list, average_prob, color = 'black', linewidth = 2, zorder = 3)
    ax1.plot(area_list, upper, color = 'black', linewidth = 1, zorder = 2, linestyle = '--')
    ax1.plot(area_list, lower, color = 'black', linewidth = 1, zorder = 2, linestyle = '--')
    
    #Calculating mean lines for the regions
    if multiple:
      first = True
      for region in regions_to_plot:
        average_prob = []
        upper = []
        lower = []
        area_list = []
        
        longest_prob = 0
        for realisation in realisation_list:
          try:
            if len(region_probs[realisation][region]) > longest_prob:
              longest_prob = len(region_probs[realisation][region])
          except NameError: 
            region_probs[realisation][region] = []
            region_x[realisation][region] = []
            
        for realisation in realisation_list:
          while len(region_probs[realisation][region]) != longest_prob:
            region_probs[realisation][region].append(0)
            
        cumulat_area = 0
        
        for i in range(longest_prob):
          average = []
          std_dev = []
  
          for realisation in realisation_list:
            average.append(region_probs[realisation][region][i])
          avg = np.mean(average)
          std_dev = np.std(average,ddof = 1)
          
          average_prob.append(avg)
          upper.append(avg + std_dev)
          lower.append(avg - std_dev)
          
          area_list.append(cumulat_area)
          cumulat_area += cell_area
          
        if first:
          ax2.plot(area_list, average_prob, color = 'black', linewidth = 2, zorder = 3)
          ax2.plot(area_list, upper, color = 'black', linewidth = 1, zorder = 2, linestyle = '--')
          ax2.plot(area_list, lower, color = 'black', linewidth = 1, zorder = 2, linestyle = '--')
          first = False
        else:
          ax3.plot(area_list, average_prob, color = 'black', linewidth = 2, zorder = 3)
          ax3.plot(area_list, upper, color = 'black', linewidth = 1, zorder = 2, linestyle = '--')
          ax3.plot(area_list, lower, color = 'black', linewidth = 1, zorder = 2, linestyle = '--')
  
  #Adding labels and other formatting for the figure
  if is_liq:
    if multiple:
      ax1.set_ylabel('Liquefaction    \nAreal Percentage    ')
      ax2.set_ylabel('Liquefaction \nAreal Percentage')
      ax3.set_ylabel('Liquefaction \nAreal Percentage')
    else:
      ax1.set_ylabel('Liquefaction Areal Percentage')
  else:
    if multiple:
      ax1.set_ylabel('Landslide    \nAreal Percentage    ')
      ax2.set_ylabel('Landslide \nAreal Percentage')
      ax3.set_ylabel('Landslide \nAreal Percentage')
    else:
      ax1.set_ylabel('Landslide Areal Percentage')
  
  ax1.set_xlabel('Total' + x_label)
  ax1.set_xscale('log')
  ax1.set_xlim((1, max_x))
  ax1.set_ylim((0,y_lim))
  
  ax1.xaxis.set_ticks_position('none')
  ax1.spines['right'].set_visible(False)
  ax1.yaxis.set_ticks_position('left')
  ax1.spines['top'].set_visible(False)
  
  #Area reference line
  if is_area:
    if max_x > 8500:
      ax1.axvline(x=LARGE_AREA, linestyle = '--')
      ax1.text(LARGE_AREA, ref_point, 'Area of the\n' + LARGE_REF + '\n (' + str(LARGE_AREA) + ' Sq.Km)', multialignment = 'center')
      ref_used = LARGE_AREA
    elif max_x > 3750:
      ax1.axvline(x=MED_AREA, linestyle = '--')
      ax1.text(MED_AREA, ref_point, 'Area of\n' + MED_REF + '\n (' + str(MED_AREA) + ' Sq.Km)', multialignment = 'center')
      ref_used = MED_AREA
    elif max_x > 850:
      ax1.axvline(x=SMALL_AREA, linestyle = '--')
      ax1.text(SMALL_AREA, ref_point, 'Area of the\n' + SMALL_REF + '\n (' + str(SMALL_AREA) + ' Sq.Km)', multialignment = 'center')
      ref_used = SMALL_AREA
    else: 
      ax1.axvline(x=VSMALL_AREA, linestyle = '--')
      ax1.text(VSMALL_AREA, ref_point, 'Area of\n' + VSMALL_REF + '\n (' + str(VSMALL_AREA) + ' Sq.Km)', multialignment = 'center')
      ref_used = VSMALL_AREA
  
  ax1.set_title(ccdf_title) 
  
  #Adding a legend if necessary
  if not mean:
    fontP = FontProperties()
    if multiple:
      if too_long:
        fontP.set_size('8.5')
      else:
        fontP.set_size('small')
      ax1.legend(loc='upper center', bbox_to_anchor=(0.5, 1.12), ncol = 3, columnspacing = 0.5, prop = fontP)
    else:
      fontP.set_size('medium')
      ax1.legend(loc='upper center',bbox_to_anchor=(0.5, 1.02), ncol = 2, columnspacing = 0.5, prop = fontP)
  
  #Formatting for sub-plots
  if multiple:
    ax2.set_xlabel(regions_to_plot[0][:-7] + x_label)
    ax3.set_xlabel(regions_to_plot[1][:-7] + x_label)
    
    ax2.set_xscale('log')
    ax2.set_xlim((1, max_x))
    ax2.set_ylim((0,y_lim))
    
    ax3.set_xscale('log')
    ax3.set_xlim((1, max_x))
    ax3.set_ylim((0,y_lim))
    
    ax2.xaxis.set_ticks_position('none')
    ax3.xaxis.set_ticks_position('none')
    
    ax2.set_title('CCDF for ' + regions_to_plot[0])
    ax3.set_title('CCDF for ' + regions_to_plot[1])
    
    if is_area:
      ax2.axvline(x = ref_used, linestyle = '--')
      ax3.axvline(x = ref_used, linestyle = '--')
  
  gs.update(wspace=0.5, hspace=0.5)
  fig = plt.gcf()
  
  fig.savefig(save_dir + file_name)
  print('Filename: \n' + file_name + '.png\n')
  
  print 'Maximum' + x_label + ': ' + str(max_x) + '\nDone\n'

if __name__ == '__main__':
  makeAllRealisationsCCDF()