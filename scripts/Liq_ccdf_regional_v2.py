'''
This has been tested for several runs on Hypocentre
Requires: xyz file of long/lat and liquefaction probability data

This script takes the xyz file and uses the information to plot liquefaction probability
against cumulative area on a ccdf. Additional plots are produced for the most effected regions.
x-axis is logarithmically scaled. There is a reference line for the area of Stewart Island. 

Usage: python Liq_ccdf_regional.py "Path to xyz file"

Writes a png of the ccdf to /Run/Impact/Liquefaction/Realisation/.

This version changes things quite a bit. First there are now functions to help readability and
to make things easier to work with. Next I switch from using a separate probability list to using
a list of lat,lng,prob tuples which lets me isolate the region for each probability.
The big change is that this version begins to work with regions.

@date 7 Dec 2017
@author Ford Wagner
@contact fwa33@canterbury.ac.nz
'''

import math
import argparse
import urllib
from geopy import Point
from geopy import distance
import matplotlib.pyplot as plt
from matplotlib import gridspec


#Reads the xyz file and returns lists of the useful data. Omits zero data.
def getxyzData(xyz, ZERO_PROB):
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
  
  
#Reads a local file of latitude/longitudes and the associated regions.
#Returns a dictionary of this region data.
def getRegionData():
  full_db = {}
  region_db_file = open('Region_database.txt')
  
  for line in region_db_file:
    line = line.split(' ')
    region = line[2]
    for i in range(3, len(line)):
      region += " " + line[i]
    full_db[(line[0],line[1])] = region[0:-8]
  region_db_file.close()
  
  return full_db

#Any lat/lng in the xyz file that isn't in the database is added to the database
def updateRegionData(full_db, full_data_list):
  region_db_file = open('Region_database.txt', 'a')
  
  for data in full_data_list:
    if (data[0],data[1]) not in full_db:
      print(prob)
      url = 'https://koordinates.com/services/query/v1/vector.json?key=d5077171350641bdb83afe4c97f3daf6&layer=4240&x=' + data[1] + '&y=' + data[0]
      urllib.urlretrieve(url, "New region data")
      filename = open('New region data')
      
      for line in filename:
        line = line.split(',')
        region = line[-2][10:-2]
        region_db_file.write(data[0] + ' ' + data[1] + ' ' + region + '\n')
      full_db[(data[0],data[1])] = region
      print(region)
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


#Generates the ccdf title and details for where to save the ccdf
def getRunDetails(xyz):
  #The name of the filepath for the xyz file
  filepath = xyz.split('/')

  #Finding correct directory to save ccdf to
  dir_to_save = ''
  for i in range(len(filepath) - 1):
    dir_to_save += "/" + filepath[i]
  dir_to_save = dir_to_save.strip('/')

  #Finding the type of data used to produce the ccdf
  xyz_name = filepath[-1].split('_')
  data_type = xyz_name[3] + "_" + xyz_name[4] + "_" + xyz_name[5]
  data_type = data_type.strip('-vs30.xyz') 
  
  #Details for the ccdf title
  run = filepath[-5] + ' '
  model = xyz_name[3] + " model, "
  map_type = xyz_name[5].strip('-vs30.xyz')
  
  ccdf_title = "Total CCDF for " + run + "(" + model + map_type + ")"
  
  return ccdf_title, dir_to_save, data_type


#Takes xyz file from the argument and turns it into a usable variable
parser = argparse.ArgumentParser()
parser.add_argument("xyz")
args = parser.parse_args()
xyz_file = open(args.xyz)

#Colours for plotting each bin
colours = ['#008b00', '#ffd700', '#ff9c00', '#ff0000']

#The zero probability value
ZERO_PROB = 0.00262 

#Upper bounds for each bin
HIGH = 0.4
MOD = 0.2
LOW = 0.1
VLOW = 0.05

#Lists to store the total probabilities and cumulatative areas in each bin
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


#Useful data from xyz file
(prob_list, lat_lng_list, full_data_list) = getxyzData(xyz_file, ZERO_PROB)

#Sorts the full_data_list by probability (low to high)
full_data_list.sort(key=lambda a:a[2])

#Dictionary of known lat/lngs and the associated region
full_db = getRegionData()

#Check the xyz file for new lat/lngs and use them to update the region_db
print('Updating the database...')
full_db = updateRegionData(full_db, full_data_list)
print('Database has been updated!')

#Get a list of impacted regions
region_list = getRegionList(full_db, full_data_list)

#Finds the size of each grid cell
cell_area = getCellSize(lat_lng_list)

total_cells = len(prob_list)
total_area = cell_area * total_cells

#Start filling the lists from the very low probability end and so start with max area
cumulat_area = total_area

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
  most_damaged_regions.append((vlow_area_dict[region][0], region))
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

#Finds basic details so that the titles are accurate and the files are saved correctly
(ccdf_title, save_dir, file_type)  = getRunDetails(args.xyz)
  

#Plotting the total CCDF
ax1 = fig.add_subplot(gs[0,:])
ax1.plot(vlow_area, vlow_prob, linewidth = 2, color = 'black')
ax1.plot(low_area, low_prob, linewidth = 2, color = colours[0])
ax1.plot(mod_area, mod_prob, linewidth = 2, color = colours[1])
ax1.plot(high_area, high_prob, linewidth = 2, color = colours[2])
ax1.plot(vhigh_area, vhigh_prob, linewidth = 2, color = colours[3])

#Title and axis labels
if len(regions_to_plot) == 2:
  ax1.set_title(ccdf_title)
  ax1.set_xlabel('Impacted Area (Sq.Km)')
else:
  ax1.set_title(ccdf_title + '\n ' + '(Only the ' + regions_to_plot[0] + ' Region Has Been Impacted)')
  ax1.set_xlabel(regions_to_plot[0] + ' Impacted Area (Sq.Km)')
ax1.set_ylabel('Liquefaction Probability')

#Plots on a logarithmic scale with certain bounds for x/y axes
ax1.set_xscale('log')
ax1.set_xlim((1, vlow_area[0]))
ax1.set_ylim((0,0.6))
ax1.xaxis.set_ticks_position('none') 

#Adding a reference line based on the impacted area
vsmall_area = 290
vsmall_ref = 'Wellington City'

small_area = 424
small_ref = 'Nelson Region'

med_area = 1760
med_ref = 'Stewart Island'

large_area = 4940
large_ref = 'Auckland Region'

if vlow_area[0] > 5500:
  ax1.axvline(x=large_area, linestyle = '--')
  ax1.text(large_area + 300, 0.43, large_ref + '\n        Area \n (' + str(large_area) + ' Sq.Km)')
  ref_used = large_area
elif vlow_area[0] > 3000:
  ax1.axvline(x=med_area, linestyle = '--')
  ax1.text(med_area + 150, 0.43, med_ref + '\n        Area \n (' + str(med_area) + ' Sq.Km)')
  ref_used = med_area
elif vlow_area[0] > 1000:
  ax1.axvline(x=small_area, linestyle = '--')
  ax1.text(small_area + 50, 0.43, small_ref + '\n        Area \n (' + str(small_area) + ' Sq.Km)')
  ref_used = small_area
else: 
  ax1.axvline(x=vsmall_area, linestyle = '--')
  ax1.text(vsmall_area + 25, 0.43, vsmall_ref + '\n        Area \n (' + str(vsmall_area) + ' Sq.Km)')
  ref_used = vsmall_area
  
#If multiple regions are impacted then plot the two most impacted regions
if len(regions_to_plot) == 2:
  #Plotting the CCDF for the most impacted region
  ax2 = fig.add_subplot(gs[1,0])
  ax2.plot(vlow_area_dict[regions_to_plot[0]], vlow_prob_dict[regions_to_plot[0]], linewidth = 2, color = 'black')
  ax2.plot(low_area_dict[regions_to_plot[0]], low_prob_dict[regions_to_plot[0]], linewidth = 2, color = colours[0])
  ax2.plot(mod_area_dict[regions_to_plot[0]], mod_prob_dict[regions_to_plot[0]], linewidth = 2, color = colours[1])
  ax2.plot(high_area_dict[regions_to_plot[0]], high_prob_dict[regions_to_plot[0]], linewidth = 2, color = colours[2])
  ax2.plot(vhigh_area_dict[regions_to_plot[0]], vhigh_prob_dict[regions_to_plot[0]], linewidth = 2, color = colours[3])
  
  #Titles and axis labels
  ax2.set_title('CCDF for ' + regions_to_plot[0] + ' Region')
  ax2.set_ylabel('Liquefaction Probability')
  ax2.set_xlabel(regions_to_plot[0] + ' Impacted Area (Sq.Km)')
  
  #The axes have the same scale/bounds as the total ccdf to help with comparison
  ax2.set_xscale('log')
  ax2.set_ylim((0, 0.6))
  ax2.set_xlim((1, vlow_area[0]))
  ax2.xaxis.set_ticks_position('none')
  
  #Adding the reference line used in the total CCDF
  ax2.axvline(x = ref_used, linestyle = '--')

  
  #Plotting the CCDF for the second most impacted region
  ax3 = fig.add_subplot(gs[1,1])
  ax3.plot(vlow_area_dict[regions_to_plot[1]], vlow_prob_dict[regions_to_plot[1]], linewidth = 2, color = 'black')
  ax3.plot(low_area_dict[regions_to_plot[1]], low_prob_dict[regions_to_plot[1]], linewidth = 2, color = colours[0])
  ax3.plot(mod_area_dict[regions_to_plot[1]], mod_prob_dict[regions_to_plot[1]], linewidth = 2, color = colours[1])
  ax3.plot(high_area_dict[regions_to_plot[1]], high_prob_dict[regions_to_plot[1]], linewidth = 2, color = colours[2])
  ax3.plot(vhigh_area_dict[regions_to_plot[1]], vhigh_prob_dict[regions_to_plot[1]], linewidth = 2, color = colours[3])
  
  #Titles and axis labels
  ax3.set_title('CCDF for ' + regions_to_plot[1] + ' Region')
  ax3.set_ylabel('Liquefaction Probability')
  ax3.set_xlabel(regions_to_plot[1] + ' Impacted Area (Sq.Km)')
  
  #Scale and bounds for the axes are the same as other CCDFs to help with comparison
  ax3.set_xscale('log')
  ax3.set_ylim((0,0.6))
  ax3.set_xlim((1, vlow_area[0]))
  ax3.xaxis.set_ticks_position('none')
  
  #Adding the reference line used in the total CCDF
  ax3.axvline(x = ref_used, linestyle = '--')


gs.update(wspace=0.5, hspace=0.5)
fig = plt.gcf()

plt.savefig("/" + save_dir + "/CCDF/Regional_CCDF_" + file_type)
#plt.savefig("Liq_ccdf_v2.png")
print
print('CCDF saved to: ' + save_dir + "/CCDF/")