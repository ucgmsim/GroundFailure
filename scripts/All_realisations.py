"""
This has been tested on v17p8.

Requires: file path to a run on Hypocentre

Note if more than 6 realisations are in the run folder then the figure will default to grey lines with a mean line.
This is to prevent the legend being too large and covering the plot.

Usage: python All_realisations.py /path/to/run --datatype --grey
Example: python All_realisations.py /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/AlpineF2K

Optional: 
--datatype: Used to specify the xyz data as liquefaction or landslide probability data.
Recognised inputs: liquefaction, liq, landslide, ls
Example: --datatype liquefaction

--grey: Used to make all lines on the plot grey and to add a black line for the mean of all the realisations.
Example: --grey grey

Writes a png of the figure to /path/to/xyz/file/dir/CCDF/
If --folder True then writes a png of the figure to the same directory that the xyz file is in

@date 15/01/2018
@author Ford Wagner
@contact fwa33@canterbury.ac.nz
"""


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

#Zero probability cutoffs for liquefaction and landslide data
LIQ_ZERO = 0.00262
LS_ZERO = 0.005

#Path from the folder of the run to the folder of the realisations
LIQ_PATH = '/Impact/Liquefaction/'
LS_PATH = '/Impact/Landslide/'

#Model that is being looked at
LIQ_MODEL = '_zhu_2016_general_probability_nz-specific-vs30.xyz'
LS_MODEL = '_jessee_2017_probability.xyz'

#Reference line information
VSMALL_AREA = 290
VSMALL_REF = 'Wellington\nCity'
  
SMALL_AREA = 445
SMALL_REF = 'Nelson\nRegion'
  
MED_AREA = 1760
MED_REF = 'Stewart\nIsland'
  
LARGE_AREA = 4940
LARGE_REF = 'Auckland\nRegion'

#Region database
REGION_DB = '/home/fordw/GroundFailure/scripts/Region_database.txt'

#Colours for plotting
COLOURS = ['#ff0000', '#ff9900', '#ffff00', '#00ff00', '#0000ff', '#ff00ff']


#Reads a local file of latitude/longitudes and the associated regions.
#Returns a dictionary of this region data.
def getRegionData():
  full_db = {}
  region_db_file = open(REGION_DB)
  
  for line in region_db_file:
    line = line.split(' ')
    try:
      region = line[2]
      for i in range(3, len(line)):
        region += " " + line[i]
      full_db[(line[0],line[1])] = region[0:-8]
    except IndexError:
      error_detected = True
  region_db_file.close()
  
  return full_db


#Calculates the area of a grid cell
def getCellSize(lat_lng):
  lat_lng.sort()
  corner1 = Point(lat_lng[0]) #lat,lng of first corner of first cell (upper LH)
  corner2 = Point(lat_lng[1]) #lat,lng of second corner of first cell (upper RH)
  lat_lng.sort(key=lambda a: (a[1], a[0])) #sorts by longitude rather than latitude
  corner3 = Point(lat_lng[1]) #lat,lng of third corner of first cell (lower LH)
  
  cell_width = distance.great_circle(corner1,corner2).km
  cell_height = distance.great_circle(corner1,corner3).km
  
  return cell_width * cell_height
  
  
#Returns a list of the regions impacted by a realisation
def getRegionList(full_db, full_data):
  region_list = []
  for data in full_data:
    region = full_db[(data[0], data[1])]
    if region not in region_list:
      region_list.append(region)
  return region_list
  

#Adds any lat/lng in the xyz file that isn't already in the database to the database
def updateRegionData(full_db, full_data):
  region_db_file = open(REGION_DB, 'a')
  
  key = 'd5077171350641bdb83afe4c97f3daf6'
  api_url = 'https://koordinates.com/services/query/v1/vector.json?'
  
  first = True
  updating = False
  
  for data in full_data:
    if (data[0],data[1]) not in full_db:
      if first:
        print 'Updating the database...'
        first = False
        updating = True
        
      print(data[2])
      url = api_url + 'key=' + key + '&layer=4240&x=' + data[1] + '&y=' + data[0]
      urllib.urlretrieve(url, "New region data")
      filename = open('New region data')
      
      for line in filename:
        line = line.split(',')
        try:
          region = line[-2][10:-2]
        except IndexError:
          print(line)
        region_db_file.write(data[0] + ' ' + data[1] + ' ' + region + '\n')
      full_db[(data[0],data[1])] = region
      print(region)
  if updating:
    print 'Updated the database!'
  return full_db
  

def main():
  #Index for selecting the colour to plot each realisation
  col_index = 0
  
  #For calculating the upper limit of the x-axis
  max_area = 0
    
  #Dictionaries for storing all probabilities and areas 
  prob_dict = {}
  area_dict = {}
  full_dict = {}
  region_probs = {}
  region_areas = {}
  
  #Dictionary of pre-processed lat/lng and region data
  full_db = getRegionData()
  
  #Creates the figure for plotting
  fig = plt.figure()
  gs = gridspec.GridSpec(2,2)
  
  
  #Processing the arguments
  parser = argparse.ArgumentParser()
  parser.add_argument('run_path')
  parser.add_argument('--datatype', default = 'liq', help = 'Specify whether the data is liquefaction or landslide')
  parser.add_argument('--grey', default = 'not grey', help = 'Creates a figure of grey lines with a black mean line')
  args = parser.parse_args()
  
  #Determining colours for plotting
  if args.grey == 'grey':
    grey = True
  else:
    if args.grey != 'not grey':
      print('To have grey lines add "grey" argument when calling this script.')
      print('Defaulting to coloured lines...')
    colours = COLOURS
    grey = False
  
  #Checks whether the datatype to plot is liquefaction or landslide and assigns zero probability
  if args.datatype == 'liq' or args.datatype == 'liquefaction':
    is_liq = True
    zero_prob = LIQ_ZERO
    model = LIQ_MODEL
  elif args.datatype == 'ls' or args.datatype == 'landslide':
    is_liq = False
    zero_prob = LS_ZERO
    model = LS_MODEL
  else:
    print 'Datatype not recognised. Please add "--datatype liquefaction" or "--datatype landslide" in argument to specify datatype.'
    quit()
  
  
  #Finds the name of the run that will be plotted (e.g. AlpineF2K)
  run_path = args.run_path.split('/')
  run = run_path[-1]
  
  #List of all realisations for the run
  if is_liq:
    path_type = LIQ_PATH
    realisation_list = os.listdir(args.run_path + path_type)
  else:
    path_type = LS_PATH
    realisation_list = os.listdir(args.run_path + path_type)
  
  #Isolating the realisations and checking whether the folder to save to exists
  if 'CCDF' in realisation_list:
    realisation_list.remove('CCDF')
    save_dir = args.run_path + path_type + 'CCDF/'
  else:
    print 'No CCDF folder found within ' + args.run_path + path_type
    print 'Please add a CCDF folder and re-run this script'
    quit()
    
  #Number of realisations - for calculating average/std dev
  num_realisations = len(realisation_list)
  
  #If more than 6 realisations then defaults to grey lines (prevents legend issues)
  if num_realisations > 6:
    print 'Too many realisations to plot in colour...'
    print 'Plotting in grey instead'
    grey = True
  
  #Variable to check for the first run through the following loop
  first_realisation = True
  
  #List to store latitude and longitude data. Only filled once as all realisations have same grid
  lat_lng = []
  
  #Filling out probability lists for each realisation
  for realisation in realisation_list:
    prob_dict[realisation] = []
    area_dict[realisation] = []
    full_data_list = []
    
    #Finding the correct xyz file for the realisation
    all_files = glob.glob(args.run_path + path_type + realisation + '/*')
    xyz_path = None
    
    for f in all_files:
      if model in f:
        xyz_path = f
    
    #If the xyz file is not found then end the script
    if xyz_path is None:
      print 'Cannot find xyz file for the model in ' + args.run_path + path_type + realisation + '/'
      quit()
      
    xyz = open(xyz_path)
    
    #Reads the xyz file and returns lists of the useful data. Omits zero data.
    i = 0
    for line in xyz:
      if i < 6:
        i += 1
      else:
        line = line.split(' ')
        prob = line[2]
        prob = prob.strip('\n')
        prob = float(prob)
        
        if first_realisation:
          lat_lng.append((line[1], line[0]))
          
        if prob >= zero_prob and not math.isnan(prob):
          prob_dict[realisation].append(prob)
          full_data_list.append((line[1],line[0],prob))
    
    if first_realisation:
      cell_area = getCellSize(lat_lng)
    
    #Sorts data lists by probability from low to high
    full_data_list.sort(key=lambda a:a[2])
    prob_dict[realisation].sort()
    
    cumulat_area = len(prob_dict[realisation]) * cell_area
    
    #Finds the upper limit for the x-axis
    if cumulat_area > max_area:
      max_area = cumulat_area
    
    #Adds areas to the area list for the realisation
    for i in range(len(prob_dict[realisation])):
      area_dict[realisation].append(cumulat_area)
      cumulat_area -= cell_area
    
    
    #Region data:
    #Adds new data from the xyz file to the dictionary of lat/lngs and regions
    full_db = updateRegionData(full_db, full_data_list)
    
    #Get a list of all the impacted regions
    region_list = getRegionList(full_db, full_data_list)
    
    #Hold data for the regions
    region_probs[realisation] = {}
    region_areas[realisation] = {}
    
    #Creates a probability and area list for each impacted region
    for region in region_list:
      region_probs[realisation][region] = []
      region_areas[realisation][region] = []
      
    #Goes through the full_data list and adds each probability to the prob list for the region
    for data in full_data_list:
      (lat,lng,prob) = (data[0], data[1], data[2])
      region = full_db[(lat,lng)]
      
      region_probs[realisation][region].append(prob)
    
    #Adds area data to the area list for each region
    for region in region_list:
      num_cells = len(region_probs[realisation][region])
      region_area = num_cells * cell_area
      
      for i in range(num_cells):
        region_areas[realisation][region].append((region_area))
        region_area -= cell_area
    
    
    #If the first model only impacts one region then figure only shows one plot
    if len(region_list) == 1 and first_realisation:
      ax1 = fig.add_subplot(gs[:,:])
      
      #Variable to determine how many plots to make
      multiple = False
    
    #If the first model impacts multiple regions then figure shows a total plot and subplots for the 2 most impacted regions
    elif first_realisation:
      #Creates a list of the regions in order of how much area will be damaged.
      regions_damaged = []
      for region in region_list:
        regions_damaged.append((region_areas[realisation][region][0], region))
      regions_damaged.sort()
      
      #Traccks the two regions which need plotting
      regions_to_plot = [regions_damaged[-1][1], regions_damaged[-2][1]]
    
      #Making the subplots
      ax1 = fig.add_subplot(gs[0,:])
      ax2 = fig.add_subplot(gs[1,0])
      ax3 = fig.add_subplot(gs[1,1])
      multiple = True
  
    
    #Plots the total ccdf for the realisation
    if grey:
      ax1.plot(area_dict[realisation], prob_dict[realisation], color = 'grey', label = realisation, zorder = 1)
    else:
      ax1.plot(area_dict[realisation], prob_dict[realisation], color = colours[col_index], label = realisation, zorder = 1)
        
    if multiple:
      if grey:
        ax2.plot(region_areas[realisation][regions_to_plot[0]], region_probs[realisation][regions_to_plot[0]], color = 'grey', zorder = 1)
      else:
        ax2.plot(region_areas[realisation][regions_to_plot[0]], region_probs[realisation][regions_to_plot[0]], color = colours[col_index], zorder = 1)
      
      #If one model only has 1 region impacted then this line will prevent an error by not trying to plot the second region
      if len(region_list) > 1:
        if grey:
          ax3.plot(region_areas[realisation][regions_to_plot[1]], region_probs[realisation][regions_to_plot[1]], color = 'grey', zorder = 1)
        else:
          ax3.plot(region_areas[realisation][regions_to_plot[1]], region_probs[realisation][regions_to_plot[1]], color = colours[col_index], zorder = 1)
          
    #Moves to the next colour
    col_index += 1
    
    first_realisation = False
  
  
  #If grey option selected then this finds the average probability of each realisation
  if grey:
    average_prob = []
    upper = []
    lower = []
    area_list = []
    
    #Determining the length of the longest probability list of all the realisations
    longest_prob = 0
    for realisation in prob_dict:
      if len(prob_dict[realisation]) > longest_prob:
        longest_prob = len(prob_dict[realisation])
          
    #Equates the lengths of the probability lists so the average can be found
    for realisation in prob_dict:
      while len(prob_dict[realisation]) != longest_prob:
        prob_dict[realisation].append(0)
      prob_dict[realisation].sort()
    
    #Total area impacted
    cumulat_area = cell_area * longest_prob
    
    #Adds the average probabilities to a list and creates an area list
    for i in range(longest_prob):
      average = []
      std_dev = []
      
      #Finds the average and standard deviation at each area point
      for realisation in prob_dict:
        average.append(prob_dict[realisation][i])
      mean = np.mean(average)
      std_dev = np.std(average,ddof = 1)
      
      #Lists to track the mean probability and the standard deviation probabilities
      average_prob.append(mean)
      upper.append(mean + std_dev)
      lower.append(mean - std_dev)
      
      #Adds each area to the area list
      area_list.append(cumulat_area)
      cumulat_area -= cell_area
      
    #Plotting a mean ccdf, and standard deviation ccdfs on the figure
    ax1.plot(area_list, average_prob, color = 'black', linewidth = 2, zorder = 3)
    ax1.plot(area_list, upper, color = 'black', linewidth = 1, zorder = 2, linestyle = '--')
    ax1.plot(area_list, lower, color = 'black', linewidth = 1, zorder = 2, linestyle = '--')
    
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
            region_areas[realisation][region] = []
        
        #Equates the lengths of the probability lists so the average can be found
        for realisation in realisation_list:
          while len(region_probs[realisation][region]) != longest_prob:
            region_probs[realisation][region].append(0)
          region_probs[realisation][region].sort()
          
        #Total area impacted
        cumulat_area = cell_area * longest_prob
        
        #Adds the average probabilities to a list and creates an area list
        for i in range(longest_prob):
          average = []
          std_dev = []
  
          #Finds the average and standard deviation at each area point
          for realisation in realisation_list:
            average.append(region_probs[realisation][region][i])
          mean = np.mean(average)
          std_dev = np.std(average,ddof = 1)
          
          #Lists to track the mean probability and the standard deviation probabilities
          average_prob.append(mean)
          upper.append(mean + std_dev)
          lower.append(mean - std_dev)
          
          #Adds each area to the area list
          area_list.append(cumulat_area)
          cumulat_area -= cell_area
          
        #Plotting a mean ccdf, and standard deviation ccdfs on the figure
        if first:
          ax2.plot(area_list, average_prob, color = 'black', linewidth = 2, zorder = 3)
          ax2.plot(area_list, upper, color = 'black', linewidth = 1, zorder = 2, linestyle = '--')
          ax2.plot(area_list, lower, color = 'black', linewidth = 1, zorder = 2, linestyle = '--')
          first = False
        else:
          ax3.plot(area_list, average_prob, color = 'black', linewidth = 2, zorder = 3)
          ax3.plot(area_list, upper, color = 'black', linewidth = 1, zorder = 2, linestyle = '--')
          ax3.plot(area_list, lower, color = 'black', linewidth = 1, zorder = 2, linestyle = '--')
    
  #Plot labels
  if is_liq:
    if not grey:
      ax1.set_ylabel('Liquefaction\nProbability')
    else:
      ax1.set_ylabel('Liquefaction Probability')
    if multiple:
      ax2.set_ylabel('Liquefaction Probability')
      ax3.set_ylabel('Liquefaction Probability')
  else:
    if not grey:
      ax1.set_ylabel('Landslide\nProbability')
    else:
      ax1.set_ylabel('Landslide Probability')
    if multiple:
      ax2.set_ylabel('Landslide Probability')
      ax3.set_ylabel('Landslide Probability')
    
  ax1.set_xlabel('Impacted Area (Sq.Km)')
  
  #Plots the x-axis on a logarithmic scale
  ax1.set_xscale('log')
  ax1.set_xlim((1, max_area))
  ax1.set_ylim((0,0.65))
  
  #Removing ticks from the x-axis
  ax1.xaxis.set_ticks_position('none')
  
  #Removes the top and right edges from the main plot so the reference line text fits
  ax1.spines['right'].set_visible(False)
  ax1.yaxis.set_ticks_position('left')
  ax1.spines['top'].set_visible(False)
  
  
  #Adding a reference line based on the impacted area
  if max_area > 8500:
    ax1.axvline(x=LARGE_AREA, linestyle = '--')
    ax1.text(LARGE_AREA, 0.37, 'Area of the\n' + LARGE_REF + '\n (' + str(LARGE_AREA) + ' Sq.Km)', multialignment = 'center')
    ref_used = LARGE_AREA
  elif max_area > 3750:
    ax1.axvline(x=MED_AREA, linestyle = '--')
    ax1.text(MED_AREA, 0.37, 'Area of\n' + MED_REF + '\n (' + str(MED_AREA) + ' Sq.Km)', multialignment = 'center')
    ref_used = MED_AREA
  elif max_area > 850:
    ax1.axvline(x=SMALL_AREA, linestyle = '--')
    ax1.text(SMALL_AREA, 0.37, 'Area of the\n' + SMALL_REF + '\n (' + str(SMALL_AREA) + ' Sq.Km)', multialignment = 'center')
    ref_used = SMALL_AREA
  else: 
    ax1.axvline(x=vsmall_area, linestyle = '--')
    ax1.text(VSMALL_AREA, 0.37, 'Area of\n' + VSMALL_REF + '\n (' + str(VSMALL_AREA) + ' Sq.Km)', multialignment = 'center')
    ref_used = VSMALL_AREA
  
  
  #Adds labels, titles, and reference line to sub_plots 
  if multiple:
    ax2.set_xlabel(regions_to_plot[0] + ' Impacted Area (Sq.Km)')
    ax3.set_xlabel(regions_to_plot[1] + ' Impacted Area (Sq.Km)')
    
    ax2.set_xscale('log')
    ax2.set_xlim((1, max_area))
    ax2.set_ylim((0,0.63))
    
    ax3.set_xscale('log')
    ax3.set_xlim((1, max_area))
    ax3.set_ylim((0,0.63))
    
    ax2.xaxis.set_ticks_position('none')
    ax3.xaxis.set_ticks_position('none')
    
    ax2.set_title('CCDF for ' + regions_to_plot[0] + ' Region')
    ax3.set_title('CCDF for ' + regions_to_plot[1] + ' Region')
    
    ax2.axvline(x = ref_used, linestyle = '--')
    ax3.axvline(x = ref_used, linestyle = '--')
  
  
  #Model details for the title
  model_details = model.split('_')
  if is_liq:
    model_name = model_details[3] + ' probability, '
    map_type = model_details[-1][0:-9]
    model_full = model_name + map_type
  else:
    model_full = 'Landslide probability ' + model_details[2]
  
  #Setting title based on type of plot requested
  if not grey:
    #Font for the legend
    fontP = FontProperties()
    fontP.set_size('small')
    
    if multiple:
      #Puts a legend at the top of the plot if plotting in colour
      ax1.legend(loc='upper center', bbox_to_anchor=(0.5, 1.12), ncol = 3, columnspacing = 0.5, prop = fontP)
      
      #Title if doing a colour plot
      ax1.set_title('CCDF for all realisations of ' + run + ' (' + model_full + ')\n')
    
    else:
      ax1.set_title('CCDF for all realisations of ' + run + '\n' + '(Only the ' + region_list[0] + ' Region Has Been Impacted)')
      
      ax1.legend(loc='upper center', ncol = 2, columnspacing = 0.5, prop = fontP)
      
    #Saving ccdf to the correct directory for the run
    file_name = 'All_Realisations.png'
    
  else:
    #Title for a grey plot
    ax1.set_title('CCDF for all Realisations of ' + run + ' with a Mean Line\n(' + model_full + ')')
    
    #Saving ccdf to the correct directory for the run
    file_name = 'Mean_All_Realisations.png'
  
  print
  print 'Saving to: ' + save_dir
  print
  
  #Formatting
  gs.update(wspace=0.5, hspace=0.5)
  fig = plt.gcf()
  
  fig.savefig(save_dir + file_name)


if __name__ == '__main__':
  main()
