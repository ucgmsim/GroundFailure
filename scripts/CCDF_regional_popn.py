'''
This has been tested for many runs on v17p8 and several runs on v17p9

Produces a CCDF of the data in the given xyz file

Requires an xyz file of space separated longitude, latitude, and probability values

Usage: python CCDF_regional_popn.py /path/to/xyz --xAxis --title --datatype --regions --save
Example: python CCDF_regional_popn.py /home/nesi00213/RunFolder/Cybershake/v17p9/Runs/AlpineF2K/Impact/Liquefaction/AlpineF2K_HYP01-21_S1244/AlpineF2K_zhu_2016_general_probability_nz-specific-vs30.xyz

Optional: 
-d, --datatype: Choose whether to use liquefaction or landslide data to plot the CCDF. Defaults to liquefaction
Example: --datatype landslide

-s, --save: Use "--save here" to save the figure to the current working directory. Otherwise will save to a CCDF directory within the realisation
Example: --save here

-x, --xAxis: Choose whether to plot area (--xAxis area), population (--xAxis pop), or dwellings (--xAxis dwell) on the x-axis. Defaults to area
Example: --xAxis pop

-r, --regions: Choose whether to remove region subplots (--regions off) or to include them (--regions on). Defaults to regions being on.
Example: --regions off

-t, --title: The title for the figure.
Example: --title This is a CCDF

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

#Lower bounds for each bin, zero probability, y-axis limit, and position of the reference line text for each datatype
LIQ_HIGH = 0.4
LIQ_MOD = 0.2
LIQ_LOW = 0.1
LIQ_VLOW = 0.05
LIQ_ZERO = 0.00262
LIQ_Y_LIM = 0.63
LIQ_REF = 0.37

LS_HIGH = 0.09
LS_MOD = 0.04
LS_LOW = 0.01
LS_VLOW = 0.025
LS_ZERO = 0.005
LS_Y_LIM = 0.35
LS_REF = 0.2

#Colours for plotting
COLOURS = ['black', '#008b00', '#ffd700', '#ff9c00', '#ff0000']

#Reference line data
VSMALL_AREA = 290
VSMALL_REF = 'Wellington\nCity' 

SMALL_AREA = 445
SMALL_REF = 'Nelson\nRegion'
  
MED_AREA = 1760
MED_REF = 'Stewart\nIsland'
  
LARGE_AREA = 4940
LARGE_REF = 'Auckland\nRegion'

#Paths to the databases 
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


def getDatatype(xyz_file, datatype):
  '''
  Returns a boolean which is true if the data is liquefaction and false if it is landslide.
  Checks the datatype by the --datatype argument first and then by the path to the xyz file if no datatype is specified.
  If no datatype can be identified then the script will end.
  '''
  if datatype == 'liq' or datatype == 'liquefaction':
    liq = True
  elif datatype == 'ls' or datatype =='landslide':
    liq = False
  else: 
    if datatype != None:
      print '"--datatype ' + datatype + '" not recognised. "liquefaction", "liq", "landslide", "ls" are recognised\nTrying to identify datatype from xyz file...\n'
    try:
      filepath = xyz_file.split('/')
      if filepath[-3] == 'Liquefaction':
        liq = True
      elif filepath[-3] == 'Landslide':
        liq = False
      else:
        print 'Cannot identify whether the data is liquefaction or landslide. Please use --datatype argument and specify "liquefaction" or "landslide"\n'
        quit()
    except IndexError:
      print 'Cannot identify whether the data is liquefaction or landslide. Please use --datatype argument and specify "liquefaction" or "landslide"\n'
      quit()
  return liq
  
  
def getTitle(xyz, title, liq, x_axis):
  '''
  Checks if a title is specified. If it isn't then the script attempts to generate one from the xyz filepath.
  Returns the title for the main CCDF
  '''
  if title != None:
    ccdf_title = ' '.join(title)
  else:
    if x_axis == 'area':
      x_axis = 'Area'
    elif x_axis == 'pop':
      x_axis = 'Population'
    else:
      x_axis = 'Dwellings'
    xyz_path = xyz.split('/')
    try:
      realisation = xyz_path[-2]
      xyz_name = xyz_path[-1].split('_')
      if liq:
        model = xyz_name[3] + " model, "
        map_type = xyz_name[5].strip('.xyz')
        ccdf_title = 'Liquefaction CCDF (' + x_axis + ') for ' + realisation + ' \n(' + model + map_type + ')'
      else:
        ccdf_title = 'Landslide CCDF (' + x_axis + ') for ' + realisation + '\n'
    except IndexError:
      print 'Cannot generate a title from the xyz filepath. Please add "--title" argument with a title for the CCDF.\n'
      quit()
  return ccdf_title
  

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
  finds the the upper left and lower left corners of another cell to get the cell height
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
    print 'Updated the database!'
  return region_dict
          

def makeCCDF():
  #Processing the arguments
  parser = argparse.ArgumentParser()
  parser.add_argument('xyz', default = None, help = 'The xyz file containing the necessary longitude, latitude, and probability data')
  parser.add_argument('-d', '--datatype', default = None, help = 'Choose whether the data is liquefaction(liq) or landslide(ls). If not specified then the script will try find the datatype from the xyz file')
  parser.add_argument('-x', '--xAxis', default = 'area', help = 'Choose whether to plot area ("-x area"), population ("-x pop"), or dwellings ("-x dwell") data on the x-axis.')
  parser.add_argument('-t', '--title', default = None, nargs = '+', help = 'Choose the title for the figure. If no title is chosen then the script will try to make a title from the name of the xyz file')
  parser.add_argument('-r', '--regions', default = 'on', help = 'Choose whether to include subplots for the impacted regions ("-r on") or not ("-r off")')
  parser.add_argument('-s', '--save', default = 'CCDF', help = 'Add "--save here" argument to save the CCDF to the current working directory. By default it saves to a CCDF directory within the folder that the xyz is saved.')
  args = parser.parse_args()
  
  #Determining whether to plot region subplots
  regions = True
  if args.regions == 'off':
    regions = False
  elif args.regions != 'on':
    print '\n"--regions ' + args.regions + '" not recognised' 
    print 'Please call the script with "--regions on" to include region subplots or with "--regions off" to remove region subplots\n'
    quit()
  
  #Determines where to save the CCDF
  xyz_path = args.xyz.strip('/').split('/')
  if args.save == 'here':
    save_dir = os.getcwd() + '/'
  elif args.save == 'CCDF':
    save_dir = '/' + '/'.join(xyz_path[:-1]) + '/CCDF/'
  else:
    print '\n"--save ' + args.save + '" not recognised. \nPlease use "--save here" to save to current working dirctory or use nothing to save to a CCDF directory within the directory that the xyz file is located\n'
    quit()
    
  print '\nFigure will save to:\n' + save_dir + '\n'
  if not os.path.isdir(save_dir):
    print save_dir + ' is not a directory. \nPlease create this directory or add "--save here" when calling the script to save to the current working directory'
    quit()
  
  liq = getDatatype(args.xyz, args.datatype)
  ccdf_title = getTitle(args.xyz, args.title, liq, args.xAxis)
    
  #Determines the data to plot on the x-axis
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
    print '\n"--xAxis ' + args.xAxis + '" not recognised \nPlease use "--xAxis area", "--xAxis pop", or "--xAxis dwell" to choose to plot area or population on the x-axis\n'
    quit()
  
  #Determining the filename
  if regions:
    if is_area:
      file_name, extension = os.path.splitext("Region_CCDF_Area_" + xyz_path[-1])
    elif is_pop:
      file_name, extension = os.path.splitext("Region_CCDF_Population_" + xyz_path[-1])
    else:
      file_name, extension = os.path.splitext("Region_CCDF_Dwellings_" + xyz_path[-1])
  else:
    if is_area:
      file_name, extension = os.path.splitext("CCDF_Area_" + xyz_path[-1])
    elif is_pop:
      file_name, extension = os.path.splitext("CCDF_Population_" + xyz_path[-1])
    else:
      file_name, extension = os.path.splitext("CCDF_Dwellings_" + xyz_path[-1])
  
  #Sets the bin lower bounds, the zero probability, y-axis limit, reference line text position, and plot type
  if liq:
    zero_prob = LIQ_ZERO
    vhigh_bound = LIQ_HIGH
    high_bound = LIQ_MOD
    mod_bound = LIQ_LOW
    low_bound = LIQ_VLOW
    y_limit = LIQ_Y_LIM
    ref_point = LIQ_REF
    plot_type = 'Liquefaction'
  else:
    zero_prob = LS_ZERO
    vhigh_bound = LS_HIGH
    high_bound = LS_MOD
    mod_bound = LS_LOW
    low_bound = LS_VLOW
    y_limit = LS_Y_LIM
    ref_point = LS_REF
    plot_type = 'Landslide'
  
  #Filling lists with the xyz data
  lat_lng, data_list = getXyzData(args.xyz, zero_prob)
  
  cell_area = getCellSize(lat_lng)
  total_cells = len(data_list)
  total_area = cell_area * total_cells
  
  #Initialise dictionaries to store data about each region
  if regions:
    reg_vhigh_prob = {}
    reg_high_prob = {}
    reg_mod_prob = {}
    reg_low_prob = {}
    reg_vlow_prob = {}
    
    reg_vhigh_x = {}
    reg_high_x = {}
    reg_mod_x = {}
    reg_low_x = {}
    reg_vlow_x = {}
    
    region_dict = getRegionData()
    region_dict = updateRegionData(region_dict, data_list)
    
    region_list = getRegionList(region_dict, data_list)
    
    #Each impacted region has a list of probabilities and a list of x-axis values
    for region in region_list:
      reg_vhigh_prob[region] = []
      reg_high_prob[region] = []
      reg_mod_prob[region] = []
      reg_low_prob[region] = []
      reg_vlow_prob[region] = []
      
      reg_vhigh_x[region] = []
      reg_high_x[region] = []
      reg_mod_x[region] = []
      reg_low_x[region] = []
      reg_vlow_x[region] = []
  
  #Lists for storing total data
  tot_vhigh_prob = []
  tot_high_prob = []
  tot_mod_prob = []
  tot_low_prob = []
  tot_vlow_prob = []
  
  tot_vhigh_x = []
  tot_high_x = []
  tot_mod_x = []
  tot_low_x = []
  tot_vlow_x = []
  
  vhigh = True
  high = True
  mod = True
  low = True
  
  #Fills high probability end first so reverse sort
  data_list.sort(reverse = True)
  
  cumulat_x = 0
  for data in data_list:
    prob, lat, lng = data[0], data[1], data[2]
    
    if regions:
      region = region_dict.get((lat,lng))
    
    if is_area:
      cumulat_x += cell_area
    #Determines the scaled population/dwelling within the grid cell based on census data
    else:
      data = data_dict.get((lat,lng))
      if data == None:
        continue
      else:
        area, pop_or_dwell = data[0], data[1]
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
    
    #Filling each bin with probability and x-axis data
    if prob >= vhigh_bound:
      tot_vhigh_prob.append(prob)
      tot_vhigh_x.append(cumulat_x)
      if regions and not is_area:
        #Stores the data as a tuple so that the pop/dwellings impacted data can be tracked
        reg_vhigh_prob[region].append((prob, scaled_PorD))
      elif regions:
        reg_vhigh_prob[region].append(prob)
        
    elif prob >= high_bound:
      #Connects the bins so that there are no gaps in the plotting
      if vhigh and len(tot_vhigh_prob) != 0:
        tot_vhigh_prob.append(prob)
        tot_vhigh_x.append(cumulat_x)
        vhigh = False
      tot_high_prob.append(prob)
      tot_high_x.append(cumulat_x)
      if regions and not is_area:
        reg_high_prob[region].append((prob, scaled_PorD))
      elif regions:
        reg_high_prob[region].append(prob)
    
    elif prob >= mod_bound:
      if high and len(tot_high_prob) != 0: 
        tot_high_prob.append(prob)
        tot_high_x.append(cumulat_x)
        high = False
      tot_mod_prob.append(prob)
      tot_mod_x.append(cumulat_x)
      if regions and not is_area:
        reg_mod_prob[region].append((prob, scaled_PorD))
      elif regions:
        reg_mod_prob[region].append(prob)
    
    elif prob >= low_bound:
      if mod and len(tot_mod_prob) != 0:
        tot_mod_prob.append(prob)
        tot_mod_x.append(cumulat_x)
        mod = False
      tot_low_prob.append(prob)
      tot_low_x.append(cumulat_x)
      if regions and not is_area:
        reg_low_prob[region].append((prob, scaled_PorD))
      elif regions:
        reg_low_prob[region].append(prob)
    
    else:
      if low and len(tot_low_prob) != 0:
        tot_low_prob.append(prob)
        tot_low_x.append(cumulat_x)
        low = False
      tot_vlow_prob.append(prob)
      tot_vlow_x.append(cumulat_x)
      if regions and not is_area:
        reg_vlow_prob[region].append((prob, scaled_PorD))
      elif regions:
        reg_vlow_prob[region].append(prob)
    
  #Adds a zero point to the highest bin which has data in it
  if len(tot_vhigh_prob) != 0:
    tot_vhigh_prob.insert(0,tot_vhigh_prob[0])
    tot_vhigh_x.insert(0,0)
  elif len(tot_high_prob) != 0:
    tot_high_prob.insert(0,tot_high_prob[0])
    tot_high_x.insert(0,0)
  elif len(tot_mod_prob) != 0:
    tot_mod_prob.insert(0,tot_mod_prob[0])
    tot_mod_x.insert(0,0)
  elif len(tot_low_prob) != 0:
    tot_low_prob.insert(0,tot_low_prob[0])
    tot_low_x.insert(0,0)
  else:
    tot_vlow_prob.insert(0,tot_vlow_prob[0])
    tot_vlow_x.insert(0,0)
  
  #Fills region area/pop/dwelling bins
  if regions:
    for region in region_list:
      vhigh = True
      high = True
      mod = True
      low = True
      cumulat_x = 0
      
      for data in reg_vhigh_prob[region]:
        if is_area:
          cumulat_x += cell_area
        else:
          cumulat_x += data[1]
        reg_vhigh_x[region].append(cumulat_x)
      
      #Adds the first point of a new bin to the previous bin so that there are no gaps in the plot
      for data in reg_high_prob[region]:
        if is_area:
          cumulat_x += cell_area
        else:
          cumulat_x += data[1]
        if vhigh and len(reg_vhigh_x[region]) != 0:
          reg_vhigh_prob[region].append(data)
          reg_vhigh_x[region].append(cumulat_x)
          vhigh = False
        reg_high_x[region].append(cumulat_x)
        
      for data in reg_mod_prob[region]:
        if is_area:
          cumulat_x += cell_area
        else:
          cumulat_x += data[1]
        if high and len(reg_high_x[region]) != 0:
          reg_high_prob[region].append(data)
          reg_high_x[region].append(cumulat_x)
          high = False
        reg_mod_x[region].append(cumulat_x)
        
      for data in reg_low_prob[region]:
        if is_area:
          cumulat_x += cell_area
        else:
          cumulat_x += data[1]
        if mod and len(reg_mod_x[region]) != 0:
          reg_mod_prob[region].append(data)
          reg_mod_x[region].append(cumulat_x)
          mod = False
        reg_low_x[region].append(cumulat_x)
        
      for data in reg_vlow_prob[region]:
        if is_area:
          cumulat_x += cell_area
        else:
          cumulat_x += data[1]
        if low and len(reg_low_x[region]) != 0:
          reg_low_prob[region].append(data)
          reg_low_x[region].append(cumulat_x)
          low = False
        reg_vlow_x[region].append(cumulat_x)
      
      #Adding zero point to highest filled bin
      if len(reg_vhigh_prob[region]) != 0:
        reg_vhigh_prob[region].insert(0,reg_vhigh_prob[region][0])
        reg_vhigh_x[region].insert(0,0)
      elif len(reg_high_prob[region]) != 0:
        reg_high_prob[region].insert(0,reg_high_prob[region][0])
        reg_high_x[region].insert(0,0)
      elif len(reg_mod_prob[region]) != 0:
        reg_mod_prob[region].insert(0,reg_mod_prob[region][0])
        reg_mod_x[region].insert(0,0)
      elif len(reg_low_prob[region]) != 0:
        reg_low_prob[region].insert(0,reg_low_prob[region][0])
        reg_low_x[region].insert(0,0)
      elif len(reg_vlow_prob[region]) != 0:
        reg_vlow_prob[region].insert(0,reg_vlow_prob[region][0])
        reg_vlow_x[region].insert(0,0)
    
    #Replaces prob, scaled pop/dwelling tuples with just the prob values in the lists
    if not is_area:
      for region in region_list:
        reg_vhigh_prob[region] = [x[0] for x in reg_vhigh_prob[region]]
        reg_high_prob[region] = [x[0] for x in reg_high_prob[region]]
        reg_mod_prob[region] = [x[0] for x in reg_mod_prob[region]]
        reg_low_prob[region] = [x[0] for x in reg_low_prob[region]]
        reg_vlow_prob[region] = [x[0] for x in reg_vlow_prob[region]]
    
    #Finds the two most impacted regions. Multiple tracks whether there are multiple plots or not
    regions_to_plot = []
    if len(region_list) == 1:
      regions_to_plot = region_list
      multiple = False
    else:
      x_region_list = []
      for region in region_list:
        if len(reg_vlow_x[region]) != 0:
          x_region_list.append((reg_vlow_x[region][-1], region))
      x_region_list.sort()
      regions_to_plot.append(x_region_list[-1][1])
      regions_to_plot.append(x_region_list[-2][1])
      multiple = True

  else:
    multiple = False
    
  #Creating the figure
  fig = plt.figure()
  if multiple:
    gs = gridspec.GridSpec(2,2)
  else:
    gs = gridspec.GridSpec(1,1)
  
  #Plotting the overall data
  ax1 = fig.add_subplot(gs[0,:])
  ax1.plot(tot_vhigh_x, tot_vhigh_prob, linewidth = 2, color = COLOURS[4])
  ax1.plot(tot_high_x, tot_high_prob, linewidth = 2, color = COLOURS[3])
  ax1.plot(tot_mod_x, tot_mod_prob, linewidth = 2, color = COLOURS[2])
  ax1.plot(tot_low_x, tot_low_prob, linewidth = 2, color = COLOURS[1])
  ax1.plot(tot_vlow_x, tot_vlow_prob, linewidth = 2, color = COLOURS[0])
  
  ax1.set_xlabel('Total' + x_label)
  ax1.set_ylabel(plot_type + ' Areal Percentage')
  ax1.set_title(ccdf_title)
  
  ax1.set_xscale('log')
  ax1.set_xlim((1, tot_vlow_x[-1]))
  ax1.set_ylim((0,y_limit))
  
  ax1.xaxis.set_ticks_position('none') 
  ax1.yaxis.set_ticks_position('left')
  ax1.spines['right'].set_visible(False)
  ax1.spines['top'].set_visible(False)
  
  #Adds an area reference line
  if is_area:
    if tot_vlow_x[-1] > 8500:
      ax1.axvline(x=LARGE_AREA, linestyle = '--')
      ax1.text(LARGE_AREA, ref_point, 'Area of the\n' + LARGE_REF + '\n (' + str(LARGE_AREA) + ' Sq.Km)', multialignment = 'center')
      ref_used = LARGE_AREA
    elif tot_vlow_x[-1] > 3750:
      ax1.axvline(x=MED_AREA, linestyle = '--')
      ax1.text(MED_AREA, ref_point, 'Area of\n' + MED_REF + '\n (' + str(MED_AREA) + ' Sq.Km)', multialignment = 'center')
      ref_used = MED_AREA
    elif tot_vlow_x[-1] > 850:
      ax1.axvline(x=SMALL_AREA, linestyle = '--')
      ax1.text(SMALL_AREA, ref_point, 'Area of the\n' + SMALL_REF + '\n (' + str(SMALL_AREA) + ' Sq.Km)', multialignment = 'center')
      ref_used = SMALL_AREA
    else: 
      ax1.axvline(x=VSMALL_AREA, linestyle = '--')
      ax1.text(VSMALL_AREA, ref_point, 'Area of\n' + VSMALL_REF + '\n (' + str(VSMALL_AREA) + ' Sq.Km)', multialignment = 'center')
      ref_used = VSMALL_AREA
  
  #Plots two subplots for the most impacted regions
  if multiple:
    ax1.set_ylabel(plot_type + ' \nAreal Percentage')
    
    ax2 = fig.add_subplot(gs[1,0])
    ax2.plot(reg_vhigh_x[regions_to_plot[0]], reg_vhigh_prob[regions_to_plot[0]], linewidth = 2, color = COLOURS[4])
    ax2.plot(reg_high_x[regions_to_plot[0]], reg_high_prob[regions_to_plot[0]], linewidth = 2, color = COLOURS[3])
    ax2.plot(reg_mod_x[regions_to_plot[0]], reg_mod_prob[regions_to_plot[0]], linewidth = 2, color = COLOURS[2])
    ax2.plot(reg_low_x[regions_to_plot[0]], reg_low_prob[regions_to_plot[0]], linewidth = 2, color = COLOURS[1])
    ax2.plot(reg_vlow_x[regions_to_plot[0]], reg_vlow_prob[regions_to_plot[0]], linewidth = 2, color = COLOURS[0])
    
    ax2.set_title('CCDF for ' + regions_to_plot[0])
    ax2.set_ylabel(plot_type + ' \nAreal Percentage')
    ax2.set_xlabel(regions_to_plot[0][:-7] + x_label)
    
    ax2.set_xscale('log')
    ax2.set_ylim((0, y_limit))
    ax2.set_xlim((1, tot_vlow_x[-1]))
    ax2.xaxis.set_ticks_position('none')
    if is_area:
      ax2.axvline(x = ref_used, linestyle = '--')
    
    ax3 = fig.add_subplot(gs[1,1])
    ax3.plot(reg_vhigh_x[regions_to_plot[1]], reg_vhigh_prob[regions_to_plot[1]], linewidth = 2, color = COLOURS[4])
    ax3.plot(reg_high_x[regions_to_plot[1]], reg_high_prob[regions_to_plot[1]], linewidth = 2, color = COLOURS[3])
    ax3.plot(reg_mod_x[regions_to_plot[1]], reg_mod_prob[regions_to_plot[1]], linewidth = 2, color = COLOURS[2])
    ax3.plot(reg_low_x[regions_to_plot[1]], reg_low_prob[regions_to_plot[1]], linewidth = 2, color = COLOURS[1])
    ax3.plot(reg_vlow_x[regions_to_plot[1]], reg_vlow_prob[regions_to_plot[1]], linewidth = 2, color = COLOURS[0])
    
    ax3.set_title('CCDF for ' + regions_to_plot[1])
    ax3.set_ylabel(plot_type + ' \nAreal Percentage')
    ax3.set_xlabel(regions_to_plot[1][:-7] + x_label)
    
    ax3.set_xscale('log')
    ax3.set_ylim((0, y_limit))
    ax3.set_xlim((1, tot_vlow_x[-1]))
    ax3.xaxis.set_ticks_position('none')
    if is_area:
      ax3.axvline(x = ref_used, linestyle = '--')
  
  gs.update(wspace=0.5, hspace=0.5)
  fig = plt.gcf()
  
  plt.savefig(save_dir + file_name)
  print('Filename: \n' + file_name + '.png\n')
  
  print 'Total' + x_label + ': ' + str(tot_vlow_x[-1])
  print 'Done\n'

if __name__ == '__main__':
  makeCCDF()
