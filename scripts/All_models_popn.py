'''
This has been tested for runs in v17p8 and several runs of v17p9

Requires: path to a realisation containing liquefaction xyz files of space separated longitude, latitude, probability values on each line

Usage: python All_models_popn.py /path/to/directory/of/xyz/files --title --xAxis --save --regions
Example: python All_models_popn.py /home/nesi00213/RunFolder/Cybershake/v17p9/Runs/AlpineF2K/Impact/Liquefaction/AlpineF2K_HYP10-21_S1514

Optional: 
-t, --title: The title for the figure.
Example: --title This is a CCDF

-s, --save: Use "--save here" to save the figure to the current working directory. Otherwise will save to a CCDF directory within the realisation
Example: --save here

-x, --xAxis: Choose whether to plot area (--xAxis area), population (--xAxis pop), or dwellings (--xAxis dwell) on the x-axis. Defaults to area
Example: --xAxis pop

-r, --regions: Choose whether to remove region subplots (--regions off) or to include them (--regions on). Defaults to regions being on.
Example: --regions off

Writes a png of the CCDF to either the current working directory, or to a CCDF directory within the realisation directory

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
import urllib
import matplotlib.pyplot as plt
from matplotlib import gridspec
import glob
from matplotlib.font_manager import FontProperties

#Models to look for within the directory. Each one that is present will be plotted
MODELS = ['_zhu_2016_coastal_probability_nz-specific-vs30.xyz', '_zhu_2016_coastal_probability_topo-based-vs30.xyz','_zhu_2016_general_probability_nz-specific-vs30.xyz', '_zhu_2016_general_probability_topo-based-vs30.xyz']

ZERO_PROB = 0.00262
Y_LIM = 0.63

#Colours for plotting
COLOURS = ['#ff0000', '#00ff00', '#0000ff', '#ff00ff']

#Reference line data
VSMALL_AREA = 290
VSMALL_REF = 'Wellington\nCity'
  
SMALL_AREA = 445
SMALL_REF = 'Nelson\nRegion'
  
MED_AREA = 1760
MED_REF = 'Stewart\nIsland'
  
LARGE_AREA = 4940
LARGE_REF = 'Auckland\nRegion'

#Database files
REGION_DB = '/home/fordw/GroundFailure/scripts/Region_database.txt'
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
  
  
def getXyzData(xyz_file):
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
        if prob >= ZERO_PROB and not math.isnan(prob):
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
  

def makeAllModelsCCDF():
  #Processing arguments
  parser = argparse.ArgumentParser()
  parser.add_argument('xyz_dir', default = None, help = 'The path to the directory of xyz files containing the longitude, latitude, and probability data')
  parser.add_argument('-t', '--title', default = None, nargs = '+', help = 'Choose the title for the figure. If no title is chosen then the script will try to make a title from the directory name of the xyz files')
  parser.add_argument('-s', '--save', default = 'CCDF', help = 'Add "--save here" argument to save the CCDF to the current working directory. By default it saves to a CCDF directory within the directory given in the xyz_dir argument.')
  parser.add_argument('-r', '--regions', default = 'on', help = 'Choose whether to include subplots for the impacted regions ("-r on") or not ("-r off")')
  parser.add_argument('-x', '--xAxis', default = 'area', help = 'Choose whether to plot area ("-x area"), population ("-x pop"), or dwellings ("-x dwell") data on the x-axis.')
  args = parser.parse_args()
  
  if args.regions == 'off':
    regions = False
  elif args.regions == 'on':
    regions = True
    region_dict = getRegionData()
  else:
    print '\n"--regions ' + args.regions + '" not recognised' 
    print 'Please call the script with "--regions on" to include region subplots or with "--regions off" to remove region subplots\n'
    quit()
  
  if args.save == 'here':
    save_dir = os.getcwd() + '/'
  elif args.save == 'CCDF':
    save_dir = '/' + args.xyz_dir.strip('/') + '/CCDF/'
  else:
    print '\n"--save ' + args.save + '" not recognised. \nPlease use "--save here" to save to current working dirctory or use nothing to save to a CCDF directory within the directory that the xyz files are located\n'
    quit()
  
  print '\nFigure will save to:\n' + save_dir + '\n'
  if not os.path.isdir(save_dir):
    print save_dir + ' is not a directory. \nPlease create this directory or add "--save here" when calling the script to save to the current working directory'
    quit()
  
  #Fills population and dwelling dictionaries if needed
  is_area = False
  is_pop = False
  if args.xAxis == 'area':
    is_area = True
    x_label = ' Impacted Area (Sq.Km)'
  elif args.xAxis == 'pop':
    x_label = ' Impacted Population'
    data_dict = getPopOrDwell('pop')
    is_pop = True
  elif args.xAxis == 'dwell':
    x_label = ' Impacted Dwellings'
    data_dict = getPopOrDwell('dwell')
  else:
    print '"--xAxis ' + args.xAxis + '" not recognised \nPlease use "--xAxis area", "--xAxis pop", or "--xAxis dwell" to choose to plot area or population on the x-axis\n'
    quit()
  
  #Finding file name and figure title
  if regions:
    if is_area:
      file_name = "All_Models_Region_CCDF_Area.png"
    elif is_pop:
      file_name = "All_Models_Region_CCDF_Population.png"
    else:
      file_name = "All_Models_Region_CCDF_Dwellings.png"
  else:
    if is_area:
      file_name = "All_Models_CCDF_Area.png"
    elif is_pop:
      file_name = "All_Models_CCDF_Population.png"
    else:
      file_name = "All_Models_CCDF_Dwellings.png"
  
  if args.title == None:
    realisation_path = args.xyz_dir.strip('/').split('/')
    if is_area:
      ccdf_title = 'Liquefaction (Area) CCDFs for all models of ' + realisation_path[-1]
    elif is_pop:
      ccdf_title = 'Liquefaction (Pop) CCDFs for all models of ' + realisation_path[-1]
    else:
      ccdf_title = 'Liquefaction (Dwell) CCDFs for all models of ' + realisation_path[-1]
  else:
    ccdf_title = ' '.join(args.title)
  
  #Checks the given directory for the xyz files for the models in MODELS
  all_files = glob.glob(args.xyz_dir + '/*')
  model_paths = []
  for model in MODELS:
    for f in all_files:
      if model in f:
        model_paths.append(f)
  
  fig = plt.figure()
  gs = gridspec.GridSpec(2,2)
  
  #Tracks colour to plot in, maximum value on the x-axis, and whether it is the first time through the loop
  col_index = 0
  max_x = 0
  first_model = True
  
  for model in model_paths:
    lat_lng, data_list = getXyzData(model)
    data_list.sort(reverse = True)
    
    #Assumes all models have the same cell_area $$$$$
    if first_model:
      cell_area = getCellSize(lat_lng)
    
    #Creates structures to store region data
    if regions:
      region_dict = updateRegionData(region_dict, data_list)
      region_list = getRegionList(region_dict, data_list)
      
      region_probs = {}
      region_x = {}
    
      for region in region_list:
        region_probs[region] = []
        region_x[region] = []
    else:
      region_list = ['None']
        
    cumulat_x = 0
    x_list = []
    prob_list = []
    
    #Stores data in total lists and region lists
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
      x_list.append(cumulat_x)
      prob_list.append(prob)
      
      #Stores probability and area/pop/dwellings tuples so that the x-axis data can be tracked
      if regions:
        region = region_dict.get((lat,lng))
        if is_area:
          region_probs[region].append((prob, cell_area))
        else:
          region_probs[region].append((prob,scaled_PorD))
    
    prob_list.insert(0,prob_list[0])
    x_list.insert(0,0)
    
    if cumulat_x > max_x:
      max_x = cumulat_x
    
    #Fills in area/pop/dwell lists for the regions
    if regions:
      for region in region_list:
        cumulat_x = 0
        for data in region_probs[region]:
          cumulat_x += data[1]
          region_x[region].append(cumulat_x)
        region_probs[region].insert(0,region_probs[region][0])
        region_x[region].insert(0,0)
        region_probs[region] = [x[0] for x in region_probs[region]]
    
    #Getting the name of the model being plotted
    model = model.split('_')
    model_type = model[-3] + ' model, ' + model[-1][0:-4]
    
    #If the first model has one impacted region then only one CCDF will be plotted, even if other models impact multiple regions
    if len(region_list) == 1 and first_model:
      ax1 = fig.add_subplot(gs[:,:])
      if regions:
        ax1.set_title(ccdf_title + ' \n(Only the ' + region_list[0][:-7] + ' Region Has Been Impacted)', fontsize = '13')
      else:
        ax1.set_title(ccdf_title + '\n', fontsize = '13')
      ax1.set_ylabel('Liquefaction Areal Percentage')
      multiple = False
      
    elif first_model:
      regions_damaged = []
      for region in region_list:
        regions_damaged.append((region_x[region][-1], region))
      regions_damaged.sort()
      regions_to_plot = [regions_damaged[-1][1], regions_damaged[-2][1]]
    
      ax1 = fig.add_subplot(gs[0,:])
      ax1.set_title(ccdf_title + '\n', fontsize = '13')
      ax1.set_ylabel('Liquefaction \nAreal Percentage')
      
      ax2 = fig.add_subplot(gs[1,0])
      ax3 = fig.add_subplot(gs[1,1])
      multiple = True
    
    #plotting
    ax1.plot(x_list, prob_list, color = COLOURS[col_index], label = model_type)
    
    if multiple:
      ax2.plot(region_x[regions_to_plot[0]], region_probs[regions_to_plot[0]], color = COLOURS[col_index], label = model_type)
      if len(region_list) > 1:
        ax3.plot(region_x[regions_to_plot[1]], region_probs[regions_to_plot[1]], color = COLOURS[col_index], label = model_type)
    
    col_index += 1
    first_model = False
  
  #Titles, labels and other formatting
  ax1.set_xlabel('Total' + x_label)
  ax1.set_xscale('log')
  ax1.set_xlim((1, max_x))
  ax1.set_ylim((0,Y_LIM))
  
  ax1.xaxis.set_ticks_position('none')
  ax1.spines['right'].set_visible(False)
  ax1.yaxis.set_ticks_position('left')
  ax1.spines['top'].set_visible(False)
  
  #Adds a legend 
  fontP = FontProperties()
  if multiple:
    fontP.set_size('small')
    ax1.legend(loc='upper center', bbox_to_anchor=(0.5, 1.12), ncol = 2, prop = fontP)
  else:
    fontP.set_size('medium')
    ax1.legend(loc='upper center', ncol = 2, prop = fontP, bbox_to_anchor=(0.49,1.02))
  
  #Area reference lines
  if is_area:  
    if max_x > 8500:
      ax1.axvline(x=LARGE_AREA, linestyle = '--')
      ax1.text(LARGE_AREA, 0.3, 'Area of the\n' + LARGE_REF + '\n (' + str(LARGE_AREA) + ' Sq.Km)', multialignment = 'center')
      ref_used = LARGE_AREA
    elif max_x > 3750:
      ax1.axvline(x=MED_AREA, linestyle = '--')
      ax1.text(MED_AREA, 0.3, 'Area of\n' + MED_REF + '\n (' + str(MED_AREA) + ' Sq.Km)', multialignment = 'center')
      ref_used = MED_AREA
    elif max_x > 850:
      ax1.axvline(x=SMALL_AREA, linestyle = '--')
      ax1.text(SMALL_AREA, 0.3, 'Area of the\n' + SMALL_REF + '\n (' + str(SMALL_AREA) + ' Sq.Km)', multialignment = 'center')
      ref_used = SMALL_AREA
    else: 
      ax1.axvline(x=VSMALL_AREA, linestyle = '--')
      ax1.text(VSMALL_AREA, 0.3, 'Area of\n' + VSMALL_REF + '\n (' + str(VSMALL_AREA) + ' Sq.Km)', multialignment = 'center')
      ref_used = VSMALL_AREA
  
  #Formatting sub-plots
  if multiple:
    ax2.set_title('CCDF for ' + regions_to_plot[0])
    ax2.set_ylabel('Liquefaction \nAreal Percentage')
    ax2.set_xlabel(regions_to_plot[0][:-7] + x_label)
    
    ax2.set_xscale('log')
    ax2.set_ylim((0,Y_LIM))
    ax2.set_xlim((1, max_x))
    ax2.xaxis.set_ticks_position('none')
    
    ax3.set_title('CCDF for ' + regions_to_plot[1])
    ax3.set_ylabel('Liquefaction \nAreal Percentage')
    ax3.set_xlabel(regions_to_plot[1][:-7] + x_label)
        
    ax3.set_xscale('log')
    ax3.set_ylim((0,Y_LIM))
    ax3.set_xlim((1, max_x))
    ax3.xaxis.set_ticks_position('none')
    
    if is_area:
      ax2.axvline(x = ref_used, linestyle = '--')
      ax3.axvline(x = ref_used, linestyle = '--')
  
  gs.update(wspace=0.5, hspace=0.5)
  fig = plt.gcf()
  
  plt.savefig(save_dir + file_name)
  print('Filename: \n' + file_name + '\n')
  
  print 'Maximum' + x_label + ': ' + str(max_x) + '\nDone\n'
  
if __name__ == '__main__':
  makeAllModelsCCDF()
