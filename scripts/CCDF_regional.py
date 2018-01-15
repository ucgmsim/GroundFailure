"""
This has been tested on several runs on Hypocentre - mostly on v17p8 data.

Requires: xyz file of lat/lng and probability data. 

Usage: python CCDF_regional.py /path/to/xyz/file --datatype --title --folder
Example: python CCDF_regional.py /home/nesi00213/RunFolder/Cybershake/v17p8/Runs/AlpineF2K/Impact/Liquefaction/AlpineF2K_HYP01-03_S1254/AlpineF2K_zhu_2016_coastal_probability_topo-based-vs30.xyz

Optional: 
--datatype: Used to specify the xyz data as liquefaction or landslide probability data.
Recognised inputs: liquefaction, liq, landslide, ls
Example: --datatype liquefaction

--title: The title for the figure.
Example: --title This is a CCDF

--folder: Use to save the figure to the same directory as the xyz file, rather than in a /CCDF/ folder. Needs "True" value to work.
Example: --folder True


Writes a png of the figure to /path/to/xyz/file/dir/CCDF/
If --folder True then writes a png of the figure to the same directory that the xyz file is in

@date 11/01/2018
@author Ford Wagner
@contact fwa33@canterbury.ac.nz
"""


import math
import argparse
import urllib
import os
from geopy import Point
from geopy import distance
import matplotlib.pyplot as plt
from matplotlib import gridspec


#Upper bounds for each bin
HIGH = 0.4
MOD = 0.2
LOW = 0.1
VLOW = 0.05

#Colours for plotting each bin
COLOURS = ['black', '#008b00', '#ffd700', '#ff9c00', '#ff0000']

#Zero probabilities for liquefaction and landslide data
LIQ_ZERO = 0.00262
LS_ZERO = 0.005

#Reference line information
VSMALL_AREA = 290
VSMALL_REF = 'Wellington\nCity'
  
SMALL_AREA = 445
SMALL_REF = 'Nelson\nRegion'
  
MED_AREA = 1760
MED_REF = 'Stewart\nIsland'
  
LARGE_AREA = 4940
LARGE_REF = 'Auckland\nRegion'

#Tracks the area exceeding this probability
EXCEED = 0.3

#Path to the region database
REGION_DB = '/home/fordw/GroundFailure/scripts/Region_database.txt'


#Checks what kind of data is being plotted. If not specified the script tries
#to identify the type from the xyz argument. Sets the zero cut-off probability
def getDataType(dataType, xyz):
  isliq = None
  if dataType is None:
    filepath = xyz.split('/')
    
    try:
      if filepath[-3] == 'Liquefaction':
        zero_prob = 0.00262
        isliq = True
      elif filepath[-3] == 'Landslide':
        zero_prob = 0.005 
        isliq = False
    except IndexError:
      isliq = None

  elif dataType == 'liquefaction' or dataType == 'liq':
    zero_prob = LIQ_ZERO
    isliq = True
  elif dataType == 'landslide' or dataType == 'ls':
    zero_prob = LS_ZERO
    isliq = False
  
  if isliq is None:
    print 'Cannot identify xyz data as liquefaction or landslide.'
    print 'Please add --dataType argument and specify liquefaction or landslide'
    quit()
  
  if isliq:
    plot_type = 'Liquefaction'
  else:
    plot_type = 'Landslide'
    
  return (zero_prob, isliq, plot_type)


#Reads the xyz file and returns lists of the useful data. Omits zero data.
def getxyzData(xyz, zero_prob):
  i = 0
  prob_list = []
  lat_lng_list = []
  full_data_list = []

  for line in xyz:
    if i < 6:
      i += 1
    else:
      line = line.split(' ')
      prob = line[2]
      prob = prob.strip('\n')
      prob = float(prob)
      
      lat_lng_list.append((line[1], line[0]))
      if prob >= zero_prob and not math.isnan(prob):
        prob_list.append(float(prob))
        full_data_list.append((line[1],line[0],prob))
  return (prob_list, lat_lng_list, full_data_list)
  

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
  
  
#Returns a list of the regions impacted
def getRegionList(full_db, full_data):
  region_list = []
  for data in full_data:
    region = full_db[(data[0], data[1])]
    if region not in region_list:
      region_list.append(region)
  return region_list
  
  
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
  #Lists to store the total probabilities and cumulative areas in each bin
  vhigh_prob = []
  high_prob = []
  mod_prob = []
  low_prob = []
  vlow_prob = []
  
  vhigh_area = []
  high_area = []
  mod_area = []
  low_area = []
  vlow_area = []
  
  #Dictionaries to store the probs/areas in each bin for each region
  vhigh_prob_dict = {}
  high_prob_dict = {}
  mod_prob_dict = {}
  low_prob_dict = {}
  vlow_prob_dict = {}
  
  vhigh_area_dict = {}
  high_area_dict = {}
  mod_area_dict = {}
  low_area_dict = {}
  vlow_area_dict = {}
  
  #These variables help track where to fill gaps in the plots
  vlow = True
  low = True
  mod = True
  high = True

  #Dictionary of known lat/lngs and the associated region
  full_db = getRegionData()
  
  
  #Reads the arguments
  parser = argparse.ArgumentParser()
  parser.add_argument("xyz")
  parser.add_argument('--datatype', nargs = '?', help = 'Specify whether the data is liquefaction (liq) or landslide (ls)')
  parser.add_argument('--title', nargs = '+', help = 'Title for the figure')
  parser.add_argument('--folder', default = 'False', help = 'Add "True" to save figure to same directory as where the xyz is')
  args = parser.parse_args()
  
  
  xyz = open(args.xyz)
  
  #Assigns the zero probability and a variable for whether the data is liquefaction
  (zero_prob, isliq, plot_type) = getDataType(args.datatype, args.xyz)
  
  #Useful data from the xyz file
  (prob_list, lat_lng_list, full_data_list) = getxyzData(xyz, zero_prob)
  
  #Sorts the full_data_list by probability (low to high)
  full_data_list.sort(key=lambda a:a[2])
  
  #Check the xyz file for new lat/lngs and use them to update the full_db
  full_db = updateRegionData(full_db, full_data_list)
  
  #Get a list of impacted regions
  region_list = getRegionList(full_db, full_data_list)
  
  #Filling the dictionaries with region:list pairs
  for region in region_list:
    vhigh_prob_dict[region] = []
    high_prob_dict[region] = []
    mod_prob_dict[region] = []
    low_prob_dict[region] = []
    vlow_prob_dict[region] = []
    
    vhigh_area_dict[region] = []
    high_area_dict[region] = []
    mod_area_dict[region] = []
    low_area_dict[region] = []
    vlow_area_dict[region] = []
    
  #Finds the size of each grid cell
  cell_area = getCellSize(lat_lng_list)
  
  total_cells = len(prob_list)
  total_area = cell_area * total_cells
  
  #Start filling the lists from the very low probability end and so start with max area
  cumulat_area = total_area
  
  
  #Tracks the area exceeding the probability in the EXCEED constant
  exceed_area = 0
  exceeded = False
    
  #Loops through the data and fills the probability and area lists. Has checks to fill in data gaps.
  #Fills the probability lists for each region. Areas for the regions are filled in later.
  for data in full_data_list:
    (lat,lng,prob) = (data[0],data[1],data[2])
    region = full_db[(lat,lng)]
    
    #Filling very low bin
    if prob <= VLOW:
      vlow_prob.append(prob)
      vlow_area.append(cumulat_area)
      vlow_prob_dict[region].append(prob)
      
    #Filling low bin. Adds first low value to the very low lists to fill in gaps.
    elif prob <= LOW:
      if vlow:
        vlow_prob.append(prob)
        vlow_area.append(cumulat_area)
        vlow = False
      low_prob.append(prob)
      low_area.append(cumulat_area)
      low_prob_dict[region].append(prob)
    
    #Filling modarate bin. Adds first mod value to the low lists to fill in gaps.
    elif prob <= MOD:
      if low:
        low_prob.append(prob)
        low_area.append(cumulat_area)
        low = False
      mod_prob.append(prob)
      mod_area.append(cumulat_area)
      mod_prob_dict[region].append(prob)
    
    #Filling high bin. Adds first high value to the mod lists to fill in gaps.
    elif prob <= HIGH:
      if mod:
        mod_prob.append(prob)
        mod_area.append(cumulat_area)
        mod = False
      high_prob.append(prob)
      high_area.append(cumulat_area)
      high_prob_dict[region].append(prob)
      
    #Filling very high bin. Adds first very high value to the high lists to fill in gaps.
    else:
      if high:
        high_prob.append(prob)
        high_area.append(cumulat_area)
        high = False
      vhigh_prob.append(prob)
      vhigh_area.append(cumulat_area)
      vhigh_prob_dict[region].append(prob)
    
    cumulat_area -= cell_area
    
    #Stores area exceeding a certain probability
    if prob >= EXCEED and not exceeded:
      exceed_area = cumulat_area
      exceeded = True
    
  
  #Checks for the highest risk bin which has data and then adds the zero point to it. Fills gaps.
  if len(vhigh_prob) != 0:
    vhigh_prob.append(vhigh_prob[-1])
    vhigh_area.append(0)
  elif len(high_prob) != 0:
    high_prob.append(high_prob[-1])
    high_area.append(0)
  elif len(mod_prob) != 0:
    mod_prob.append(mod_prob[-1])
    mod_area.append(0)
  elif len(low_prob) != 0:
    low_prob.append(low_prob[-1])
    low_area.append(0)
  else:
    vlow_prob.append(vlow_prob[-1])
    vlow_area.append(0)
    
  #Goes through and fills the area lists for each region. Has gap fill checks similar to the above.
  for region in region_list:
    vlow = True
    low = True
    mod = True
    high = True
  
    #Total area in the region which is impacted.
    cumulat_area = (len(vlow_prob_dict[region]) + len(low_prob_dict[region]) + len(mod_prob_dict[region]) + len(high_prob_dict[region]) + len(vhigh_prob_dict[region]                    )) * cell_area
    
    #Fills very low area list
    for i in range(len(vlow_prob_dict[region])):
      vlow_area_dict[region].append(cumulat_area)
      cumulat_area -= cell_area
    
    #Fills low area list. Adds first low value to very low area list (gap filling)
    for i in range(len(low_prob_dict[region])):
      if vlow:
        vlow_prob_dict[region].append(low_prob_dict[region][0])
        vlow_area_dict[region].append(cumulat_area)
        vlow = False
      low_area_dict[region].append(cumulat_area)
      cumulat_area -= cell_area
    
    #Fills modarate area list. Adds first mod value to low area list (gap filling)
    for i in range(len(mod_prob_dict[region])):
      if low:
        low_prob_dict[region].append(mod_prob_dict[region][0])
        low_area_dict[region].append(cumulat_area)
        low = False
      mod_area_dict[region].append(cumulat_area)
      cumulat_area -= cell_area
      
    #Fills high area list. Adds first high value to mod area list (gap filling)
    for i in range(len(high_prob_dict[region])):
      if mod:
        mod_prob_dict[region].append(high_prob_dict[region][0])
        mod_area_dict[region].append(cumulat_area)
        mod = False
      high_area_dict[region].append(cumulat_area)
      cumulat_area -= cell_area
      
    #Fills very high area list. Adds first very high value to high area list (gap filling)
    for i in range(len(vhigh_prob_dict[region])):
      if high:
        high_prob_dict[region].append(vhigh_prob_dict[region][0])
        high_area_dict[region].append(cumulat_area)
        high = False
      vhigh_area_dict[region].append(cumulat_area)
      cumulat_area -= cell_area
      
    #Checks for the highest risk bin which has data and then adds the zero point to it. Fills gaps.
    if len(vhigh_prob_dict[region]) != 0:
      vhigh_prob_dict[region].append(vhigh_prob_dict[region][-1])
      vhigh_area_dict[region].append(0)
    elif len(high_prob_dict[region]) != 0:
      high_prob_dict[region].append(high_prob_dict[region][-1])
      high_area_dict[region].append(0)
    elif len(mod_prob_dict[region]) != 0:
      mod_prob_dict[region].append(mod_prob_dict[region][-1])
      mod_area_dict[region].append(0)
    elif len(low_prob_dict[region]) != 0:
      low_prob_dict[region].append(low_prob_dict[region][-1])
      low_area_dict[region].append(0)
    else:
      vlow_prob_dict[region].append(vlow_prob_dict[region][-1])
      vlow_area_dict[region].append(0)
    
    
  #Creates a list of the regions in order of how much area will be impacted.
  most_damaged_regions = []
  for region in region_list:
    try:
      most_damaged_regions.append((vlow_area_dict[region][0], region))
    except IndexError:
      if len(low_area_dict[region] > 0):
        most_damaged_regions.append((low_area_dict[region][0], region))
      elif len(mod_area_dict[region] > 0):
        most_damaged_regions.append((mod_area_dict[region][0], region))
      elif len(high_area_dict[region] > 0):
        most_damaged_regions.append((high_area_dict[region][0], region))
      else:
        most_damaged_regions.append((vhigh_area_dict[region][0], region))
  most_damaged_regions.sort()
  
  #Finds region with most area impacted so it can be plotted
  regions_to_plot = []
  regions_to_plot.append(most_damaged_regions[-1][1])
  
  #If multiple regions are damaged then this finds the second most impacted region
  if len(most_damaged_regions) > 1:
    regions_to_plot.append(most_damaged_regions[-2][1])
    
    
  #Plotting
  fig = plt.figure()
  
  #If multiple regions are damaged then plots two regions, otherwise plots the one damaged region.
  if len(regions_to_plot) == 1:
    gs = gridspec.GridSpec(1,1)
  else:
    gs = gridspec.GridSpec(2,2)
  
  #Determining the directory to save the figure to
  xyz_path = args.xyz.split('/')
  if len(xyz_path) == 1:
    #If xyz is in the current working directory
    save_dir = os.getcwd()
  else:
    save_dir = xyz_path[0]
    for i in range(len(xyz_path) - 2):
      save_dir += '/' + xyz_path[i + 1]  
  
  #Determining the title of the figure
  if args.title is None:
    try:
      xyz_name = xyz_path[-1].split('_')
      run = xyz_path[-5]
      
      if isliq:
        model = xyz_name[3] + " model, "
        map_type = xyz_name[5].strip('-vs30.xyz')
        ccdf_title = 'Total Liquefaction CCDF for ' + run + ' (' + model + map_type + ')'
      else:
        ccdf_title = 'Total Landslide CCDF for ' + run
  
    except IndexError:
      print
      print 'Cannot find title from xyz filepath'
      print 'Please specify a title with the --title argument'
      quit()
    
  else:
    ccdf_title = ' '.join(args.title)
  
  #The name that the figure is saved under is built from the name of the xyz file
  file_name, extension = os.path.splitext("/Regional_CCDF_" + xyz_path[-1])
  
  
  #Plotting the total CCDF
  ax1 = fig.add_subplot(gs[0,:])
  ax1.plot(vlow_area, vlow_prob, linewidth = 2, color = COLOURS[0])
  ax1.plot(low_area, low_prob, linewidth = 2, color = COLOURS[1])
  ax1.plot(mod_area, mod_prob, linewidth = 2, color = COLOURS[2])
  ax1.plot(high_area, high_prob, linewidth = 2, color = COLOURS[3])
  ax1.plot(vhigh_area, vhigh_prob, linewidth = 2, color = COLOURS[4])
  
  #Title and axis labels
  if len(regions_to_plot) == 2:
    ax1.set_title(ccdf_title + '\n')
    ax1.set_xlabel('Impacted Area (Sq.Km)')
  else:
    ax1.set_title(ccdf_title + '\n ' + '(Only the ' + regions_to_plot[0] + ' Region Has Been Impacted)')
    ax1.set_xlabel(regions_to_plot[0] + ' Impacted Area (Sq.Km)')
  ax1.set_ylabel(plot_type + ' Probability')
  
  #Plots on a logarithmic scale with certain bounds for x/y axes
  ax1.set_xscale('log')
  ax1.set_xlim((1, vlow_area[0]))
  ax1.set_ylim((0,0.63))
  
  #Removes ticks on the axes
  ax1.xaxis.set_ticks_position('none') 
  ax1.yaxis.set_ticks_position('left')
  ax1.spines['right'].set_visible(False)
  ax1.spines['top'].set_visible(False)
  
  
  #Adding a reference line based on the impacted area
  if vlow_area[0] > 8500:
    ax1.axvline(x=LARGE_AREA, linestyle = '--')
    ax1.text(LARGE_AREA, 0.37, 'Area of the\n' + LARGE_REF + '\n (' + str(LARGE_AREA) + ' Sq.Km)', multialignment = 'center')
    ref_used = LARGE_AREA
  elif vlow_area[0] > 3750:
    ax1.axvline(x=MED_AREA, linestyle = '--')
    ax1.text(MED_AREA, 0.37, 'Area of\n' + MED_REF + '\n (' + str(MED_AREA) + ' Sq.Km)', multialignment = 'center')
    ref_used = MED_AREA
  elif vlow_area[0] > 850:
    ax1.axvline(x=SMALL_AREA, linestyle = '--')
    ax1.text(SMALL_AREA, 0.37, 'Area of the\n' + SMALL_REF + '\n (' + str(SMALL_AREA) + ' Sq.Km)', multialignment = 'center')
    ref_used = SMALL_AREA
  else: 
    ax1.axvline(x=vsmall_area, linestyle = '--')
    ax1.text(VSMALL_AREA, 0.37, 'Area of\n' + VSMALL_REF + '\n (' + str(VSMALL_AREA) + ' Sq.Km)', multialignment = 'center')
    ref_used = VSMALL_AREA
    
  #If multiple regions are impacted then plot the two most impacted regions
  if len(regions_to_plot) == 2:
    #Plotting the CCDF for the most impacted region
    ax2 = fig.add_subplot(gs[1,0])
    ax2.plot(vlow_area_dict[regions_to_plot[0]], vlow_prob_dict[regions_to_plot[0]], linewidth = 2, color = COLOURS[0])
    ax2.plot(low_area_dict[regions_to_plot[0]], low_prob_dict[regions_to_plot[0]], linewidth = 2, color = COLOURS[1])
    ax2.plot(mod_area_dict[regions_to_plot[0]], mod_prob_dict[regions_to_plot[0]], linewidth = 2, color = COLOURS[2])
    ax2.plot(high_area_dict[regions_to_plot[0]], high_prob_dict[regions_to_plot[0]], linewidth = 2, color = COLOURS[3])
    ax2.plot(vhigh_area_dict[regions_to_plot[0]], vhigh_prob_dict[regions_to_plot[0]], linewidth = 2, color = COLOURS[4])
    
    #Titles and axis labels
    ax2.set_title('CCDF for ' + regions_to_plot[0] + ' Region')
    ax2.set_ylabel(plot_type + ' Probability')
    ax2.set_xlabel(regions_to_plot[0] + ' Impacted Area (Sq.Km)')
    
    #The axes have the same scale/bounds as the total ccdf to help with comparison
    ax2.set_xscale('log')
    ax2.set_ylim((0, 0.63))
    ax2.set_xlim((1, vlow_area[0]))
    ax2.xaxis.set_ticks_position('none')
    
    #Adding the reference line used in the total CCDF
    ax2.axvline(x = ref_used, linestyle = '--')
  
    
    #Plotting the CCDF for the second most impacted region
    ax3 = fig.add_subplot(gs[1,1])
    ax3.plot(vlow_area_dict[regions_to_plot[1]], vlow_prob_dict[regions_to_plot[1]], linewidth = 2, color = COLOURS[0])
    ax3.plot(low_area_dict[regions_to_plot[1]], low_prob_dict[regions_to_plot[1]], linewidth = 2, color = COLOURS[1])
    ax3.plot(mod_area_dict[regions_to_plot[1]], mod_prob_dict[regions_to_plot[1]], linewidth = 2, color = COLOURS[2])
    ax3.plot(high_area_dict[regions_to_plot[1]], high_prob_dict[regions_to_plot[1]], linewidth = 2, color = COLOURS[3])
    ax3.plot(vhigh_area_dict[regions_to_plot[1]], vhigh_prob_dict[regions_to_plot[1]], linewidth = 2, color = COLOURS[4])
    
    #Titles and axis labels
    ax3.set_title('CCDF for ' + regions_to_plot[1] + ' Region')
    ax3.set_ylabel(plot_type + ' Probability')
    ax3.set_xlabel(regions_to_plot[1] + ' Impacted Area (Sq.Km)')
    
    #Scale and bounds for the axes are the same as other CCDFs to help with comparison
    ax3.set_xscale('log')
    ax3.set_ylim((0,0.63))
    ax3.set_xlim((1, vlow_area[0]))
    ax3.xaxis.set_ticks_position('none')
    
    #Adding the reference line used in the total CCDF
    ax3.axvline(x = ref_used, linestyle = '--')
  
  
  gs.update(wspace=0.5, hspace=0.5)
  fig = plt.gcf()
  
  #Prints where the file is being saved to
  print
  if args.folder != 'False' and args.folder != 'True':
    print 'To save the figure to the same directory as where the xyz is located add the "--folder True" argument'
    save_dir += '/' + 'CCDF'
    
    
  #Saves to the correct directory based on the data type
  try:
    plt.savefig(save_dir + file_name)
    print('Saving to: ' + save_dir)
  except IOError:
    print 'No /CCDF/ directory exists. Please add the directory or add --folder True argument'
    
  print
  print 'Area exceeding a probability of ' + str(EXCEED) + ':'
  print str(exceed_area) + ' Sq.Km'
  print
  
if __name__ == '__main__':
  main()
