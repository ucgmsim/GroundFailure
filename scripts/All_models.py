'''
This has been tested for several runs on Hypocentre. All of the testing was done on v17p8.
If new models are used then make sure to update the MODELS constant.

Requires: Path to a folder containing xyz files of the data for at least one of the 4 models.
The models are specified in the MODELS constant (line 38)

Note: A CCDF directory must exist within the directory containing the xyz files
or else the --folder optional argument is needed for the script to function.

This script takes the path to the folder and produces a single figure with CCDFs for
the data from each model. If two or more regions are impacted by the FIRST model then
the script will output a figure with subplots for the two most impacted regions.

Usage: python All_models.py "path/to/folder/of/xyz/files" --title --folder
example: python All_models.py /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/AlpineF2K/Impact/Liquefaction/AlpineF2K_HYP01-03_S1254

Optional: --title argument - Add the desired figure title as an argument
Default: Uses the first argument to derive a title

Optional: --folder argument - Add "--folder True" when calling the script to save the figure to the same directory as the xyz files.

Writes a png of the figure to /path/to/folder/of/xyz/files/CCDF/

@date 11/01/2018
@author Ford Wagner
@contact fwa33@canterbury.ac.nz
'''

import argparse
import glob
import math
from geopy import Point
from geopy import distance
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.font_manager import FontProperties
import urllib


#List of all the models
MODELS = ['_zhu_2016_coastal_probability_nz-specific-vs30.xyz', '_zhu_2016_coastal_probability_topo-based-vs30.xyz','_zhu_2016_general_probability_nz-specific-vs30.xyz', '_zhu_2016_general_probability_topo-based-vs30.xyz']

#Ignore all data below this probability
ZERO_PROB = 0.00262

#List of colours for plotting
COLOURS = ['#ff0000', '#00ff00', '#0000ff', '#ff00ff']

#Reference lines
VSMALL_AREA = 290
VSMALL_REF = 'Wellington\nCity'
  
SMALL_AREA = 445
SMALL_REF = 'Nelson\nRegion'
  
MED_AREA = 1760
MED_REF = 'Stewart\nIsland'
  
LARGE_AREA = 4940
LARGE_REF = 'Auckland\nRegion'


#Reads a local file of latitude/longitudes and the associated regions.
#Returns a dictionary of this region data.
def getRegionData():
  full_db = {}
  region_db_file = open('Region_database.txt')
  
  for line in region_db_file:
    line = line.split(' ')
    
    #Checks for any errors in the database
    try:
      region = line[2]
      for i in range(3, len(line)):
        region += " " + line[i]
      full_db[(line[0],line[1])] = region[0:-8]
    except IndexError:
      print 
  region_db_file.close()
  
  return full_db


#Reads an xyz file and returns lists of the useful data. Omits zero data.
def getxyzData(xyz_file):
  i = 0
  prob_list = []
  lat_lng_list = []
  full_data_list = []

  for line in xyz_file:
    if i < 6:
      i += 1
    else:
      line = line.split(' ')
      prob = line[2]
      prob = prob.strip('\n')
      prob = float(prob)
      
      lat_lng_list.append((line[1], line[0]))
      if prob >= ZERO_PROB and not math.isnan(prob):
        prob_list.append(float(prob))
        full_data_list.append((line[1],line[0],prob))
  return (prob_list, lat_lng_list, full_data_list)
  

#Returns the area of a grid cell
def getCellSize(lat_lng):
  lat_lng.sort()
  corner1 = Point(lat_lng[0]) #lat,lng of first corner of first cell (upper LH)
  corner2 = Point(lat_lng[1]) #lat,lng of second corner of first cell (upper RH)
  lat_lng.sort(key=lambda a: (a[1], a[0])) #sorts by longitude rather than latitude
  corner3 = Point(lat_lng[1]) #lat,lng of third corner of first cell (lower LH)
  
  cell_width = distance.great_circle(corner1,corner2).km
  cell_height = distance.great_circle(corner1,corner3).km
  
  #Returns the cell area in km^2
  return cell_width * cell_height
  

#Returns a list of the regions impacted
def getRegionList(full_db, full_data):
  region_list = []
  for data in full_data:
    region = full_db[(data[0], data[1])]
    if region not in region_list:
      region_list.append(region)
  return region_list
  

#Adds any lat/lng in the xyz file that isn't already in the database to the database
def updateRegionData(full_db, full_data):
  region_db_file = open('Region_database.txt', 'a')
  
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
  #Index for selecting the colour to plot each line
  col_index = 0
  
  #Creates the figure for plotting
  fig = plt.figure()
  gs = gridspec.GridSpec(2,2)
  
  #Fills up a dictionary with pre-processed lat/lng and region data
  full_db = getRegionData()
  
  
  #Takes the path to the realisation and makes it a usable variable
  parser = argparse.ArgumentParser()
  parser.add_argument('xyz_dir', help = 'Directory containing the xyz files')
  parser.add_argument('--title', help = 'Title for the figure', nargs = '+', default = 'None given')
  parser.add_argument('--folder', help = 'Set to True to save figure to directory containing the xyz files', default = False)
  args = parser.parse_args()
  
  #Checks if title is given as an argument, if not tries to generate a title
  if args.title == 'None given':
    realisation_path = args.xyz_dir
    realisation_path = realisation_path.strip('/')
    realisation_path = realisation_path.split('/')
    
    realisation = realisation_path[-1]
    
    ccdf_title = 'Liquefaction CCDFs for all models of ' + realisation
    
  else:
    ccdf_title = ''
    ccdf_title = ' '.join(args.title)
    #for word in args.title:
      #ccdf_title += word + ' '
  
  #Finds all files within the realisation's directory
  all_files = glob.glob(args.xyz_dir + '/*')
  
  #List for storing the paths to the xyz files for each model
  model_paths = []
  
  #Adds the desired xyz files to the model_path list
  for model in MODELS:
    for f in all_files:
      if model in f:
        model_paths.append(f)
  
  
  #Tracks the max area impacted across the models
  max_area = 0
  
  #Variable to check whether the following loop is on the first iteration
  first_model = True
  
  for model in model_paths:
    #Opens the xyz file for the model
    xyz = open(model)
    
    #Extracts useful data from xyz file: prob_list contains only probabilities
    #lat_lng contains all latitude/longitudes of the grid in order
    #full_data contains the lat/lng and its associated probability
    (prob_list, lat_lng, full_data) = getxyzData(xyz)
    
    #Sorts the data from low to high by probability
    full_data.sort(key=lambda a:a[2])
    prob_list.sort()
    
    #Finds the size of each grid cell using the lat_lng data
    cell_area = getCellSize(lat_lng)
    
    #Total area to consider
    cumulat_area = cell_area * len(prob_list)
    area_list = []
    
    #Adds areas in a parallel list to the probability list
    for i in range(len(prob_list)):
      area_list.append((cumulat_area))
      cumulat_area -= cell_area
    
    #Finds max area across the models - upper bound for x-axis
    if area_list[0] > max_area:
      max_area = area_list[0]
    
    #Region data:
    #Adds new data from the xyz file to the dictionary of lat/lngs and regions
    full_db = updateRegionData(full_db, full_data)
    
    #Get a list of all the impacted regions
    region_list = getRegionList(full_db, full_data)
    
    #Hold data for the regions
    region_probs = {}
    region_areas = {}
    
    #Creates a probability and area list for each impacted region
    for region in region_list:
      region_probs[region] = []
      region_areas[region] = []
      
    #Goes through the full_data list and adds each probability to the prob list for the region
    for data in full_data:
      (lat,lng,prob) = (data[0], data[1], data[2])
      region = full_db[(lat,lng)]
      
      region_probs[region].append(prob)
  
    #Adds area data to the area list for each region
    for region in region_list:
      num_cells = len(region_probs[region])
      region_area = num_cells * cell_area
      
      for i in range(num_cells):
        region_areas[region].append((region_area))
        region_area -= cell_area
    
    
    #Identifies the type of model from the xyz file path (depends on MODELS)
    model = model.split('_')
    model_type = model[-3] + ' model, ' + model[-1][0:-9]
    
    
    #If the first model only impacts one region then plots data on one graph
    if len(region_list) == 1 and first_model:
      ax1 = fig.add_subplot(gs[:,:])
      ax1.set_title(ccdf_title + '\n' + '(Only the ' + region_list[0] + ' Region Has Been Impacted)')
      
      #Variable to determine how many plots
      multiple = False
    
    #If the first model impacts multiple regions then plots the total and the 2 most impacted regions
    elif first_model:
      #Creates a list of the regions in order of how much area will be damaged.
      regions_damaged = []
      for region in region_list:
        regions_damaged.append((region_areas[region][0], region))
      regions_damaged.sort()
      
      regions_to_plot = [regions_damaged[-1][1], regions_damaged[-2][1]]
    
    
      ax1 = fig.add_subplot(gs[0,:])
      ax1.set_title(ccdf_title + '\n')
      
      ax2 = fig.add_subplot(gs[1,0])
      ax3 = fig.add_subplot(gs[1,1])
      multiple = True
      
    
    #Plots the total ccdf for the model. All models are plotted on this plot
    ax1.plot(area_list, prob_list, color = COLOURS[col_index], label = model_type)
    
    if multiple:
      ax2.plot(region_areas[regions_to_plot[0]], region_probs[regions_to_plot[0]], color = COLOURS[col_index], label = model_type)
      
      #If one model only has 1 region impacted then this line will prevent an error
      if len(region_list) > 1:
        ax3.plot(region_areas[regions_to_plot[1]], region_probs[regions_to_plot[1]], color = COLOURS[col_index], label = model_type)
    
    #Move onto next colour
    col_index += 1
    
    #No longer the first iteration of the loop
    first_model = False
      
  
  #Titles and axis labels
  ax1.set_ylabel('Liquefaction probability')
  ax1.set_xlabel('Impacted Area (Sq.Km)')
  
  #Plots on a logarithmic scale and sets bounds for the x/y axes
  ax1.set_xscale('log')
  ax1.set_xlim((1, max_area))
  ax1.set_ylim((0,0.63))
  
  #Removing ticks from the x-axis
  ax1.xaxis.set_ticks_position('none')
  
  #Font for the legend
  fontP = FontProperties()
  
  if multiple:
    fontP.set_size('small')
    #Puts a legend in the lower left corner of the plot - small realisations move this
    ax1.legend(loc='upper center', bbox_to_anchor=(0.5, 1.12), ncol = 2, prop = fontP)
  
  else:
    fontP.set_size('medium')
    #Puts a legend in the lower left corner of the plot
    ax1.legend(loc='upper center', ncol = 2, prop = fontP, bbox_to_anchor=(0.5,1.01))
  
  
  #Adding a reference line based on the impacted area
  if vlow_area[0] > 8500:
    ax1.axvline(x=LARGE_AREA, linestyle = '--')
    ax1.text(LARGE_AREA, 0.3, 'Area of the\n' + LARGE_REF + '\n (' + str(LARGE_AREA) + ' Sq.Km)', multialignment = 'center')
    ref_used = LARGE_AREA
  elif vlow_area[0] > 3750:
    ax1.axvline(x=MED_AREA, linestyle = '--')
    ax1.text(MED_AREA, 0.3, 'Area of\n' + MED_REF + '\n (' + str(MED_AREA) + ' Sq.Km)', multialignment = 'center')
    ref_used = MED_AREA
  elif vlow_area[0] > 850:
    ax1.axvline(x=SMALL_AREA, linestyle = '--')
    ax1.text(SMALL_AREA, 0.3, 'Area of the\n' + SMALL_REF + '\n (' + str(SMALL_AREA) + ' Sq.Km)', multialignment = 'center')
    ref_used = SMALL_AREA
  else: 
    ax1.axvline(x=vsmall_area, linestyle = '--')
    ax1.text(VSMALL_AREA, 0.3, 'Area of\n' + VSMALL_REF + '\n (' + str(VSMALL_AREA) + ' Sq.Km)', multialignment = 'center')
    ref_used = VSMALL_AREA
    
  #Removes the top and right edges from the main plot so the reference line text fits
  ax1.spines['right'].set_visible(False)
  ax1.yaxis.set_ticks_position('left')
  ax1.spines['top'].set_visible(False)
  
  
  #Titles, labels, scale, bounds, and x-axis ticks for other plots
  #Also adds the reference line to the subplots
  if multiple:
    ax2.set_title('CCDF for ' + regions_damaged[-1][1] + ' Region')
    ax2.set_ylabel('Liquefaction Probability')
    ax2.set_xlabel(regions_damaged[-1][1] + ' Impacted Area (Sq.Km)')
    
    ax2.set_xscale('log')
    ax2.set_ylim((0,0.63))
    ax2.set_xlim((1, max_area))
    ax2.xaxis.set_ticks_position('none')
    
    ax2.axvline(x = ref_used, linestyle = '--')
    
    
    ax3.set_title('CCDF for ' + regions_damaged[-2][1] + ' Region')
    ax3.set_ylabel('Liquefaction Probability')
    ax3.set_xlabel(regions_damaged[-2][1] + ' Impacted Area (Sq.Km)')
        
    ax3.set_xscale('log')
    ax3.set_ylim((0,0.63))
    ax3.set_xlim((1, max_area))
    ax3.xaxis.set_ticks_position('none')
    
    ax3.axvline(x = ref_used, linestyle = '--')
    
  
  #Formatting
  gs.update(wspace=0.5, hspace=0.5)
  fig = plt.gcf()
  
  #Saving ccdf to the realisation directory
  print
  if args.folder == 'True':
    print 'Saving to: ' + args.xyz_dir + '/All_models_CCDF.png'
    print
    fig.savefig(args.xyz_dir + '/All_models_CCDF.png')
  else:
    if args.folder != False:
      print 'To save figure to same directory as the xyz files add --folder True argument'
    print 'Saving to: ' + args.xyz_dir + '/CCDF/All_models_CCDF.png'
    print
    try:
      fig.savefig(args.xyz_dir + '/CCDF/All_models_CCDF.png')
    except IOError:
      print "Error: No /CCDF/ directory. Please add the directory or use the --folder True argument"
  
if __name__ == '__main__':
  main()