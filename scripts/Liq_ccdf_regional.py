'''
This has been tested for several runs on Hypocentre
Requires: xyz file of long/lat and liquefaction probability data

This script takes the xyz file and uses the information to plot liquefaction probability
against cumulative area on a ccdf. Additional plots are produced for the most effected regions.
x-axis is logarithmically scaled. There is a reference line for the area of Stewart Island. 

Usage: python Liq_ccdf_regional.py "Path to xyz file"

Writes a png of the ccdf to current working directory.

This version changes things quite a bit. First there are now functions to help readability and
to make things easier to work with. Next I switch from using a separate probability list to using
a list of lat,lng,prob tuples which lets me isolate the region for each probability.
The big change is that this version begins to work with regions.

@date 7 Dec 2017
@author Ford Wagner
@contact fwa33@canterbury.ac.nz
'''

import argparse
import urllib
from geopy import Point
from geopy import distance
import matplotlib.pyplot as plt
from matplotlib import gridspec

#Extracts data from the xyz file
def getDataLists(xyz):
  i = 0
  total_pts = 0
  data_list = []
  prob_list = []
  lat_lng = []
  
  for line in xyz:
    #Ignores first 6 lines of xyz file
    if i <6:
      i += 1
    else:
      line = line.split(" ")
      prob = line[2]
      prob = prob.strip('\n')
      prob = float(prob)
      
      #Data list keeps lat,lng and prob data together
      #Prob list holds all probabilities for easy sorting
      #lat,lng holds all lat,lngs for determining the grid size
      data_list.append((line[1], line[0], prob))
      prob_list.append(prob)
      lat_lng.append((line[1],line[0]))
  return data_list, prob_list, lat_lng


#Gives size of each grid cell, useful for determining cumulative area on CCDF
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
  
  
#Creates a dictionary from a local database of lat/lngs and associated regions.
#The lat/lngs are the keys and the region is the value.
def getFullDB():
  full_db = {}
  region_db = open('Region_database.txt')
  
  for line in region_db:
    line = line.split(' ')
    region = line[2]
    for i in range(3, len(line)):
      region += " " + line[i]
    region = region.strip(' Region\n')
    full_db[(line[0],line[1])] = region
  region_db.close()
  
  #Returns a dictionary of ALL pre-processed lat/lngs with associated regions
  return full_db
  
  
#Checks if any long/lats in the given grid are not in the database and then updates the database on hypocentre.
#Returns a full dictionary of long/lat : region pairs
def fillRegionDB(full_db, region_db, lat, lng, prob):
  #Checks for values on land that are not already in the database
  if (lat,lng) not in full_db and prob >= 0.00262:
    url = 'https://koordinates.com/services/query/v1/vector.json?key=d5077171350641bdb83afe4c97f3daf6&layer=4240&x=' + lng + '&y=' + lat
    urllib.urlretrieve(url, "region thing")
    filename = open('region thing')
    
    #Writes the new data to the database in the correct format
    for line in filename:
      line = line.split(',')
      region = line[-2][10:-2]
      if region[-1] != 'n':
        region_db.write(lat + ' ' + lng + ' No Region Data' + '\n')
      else:
        region_db.write(lat + ' ' + lng + ' ' + region + '\n')
    #Adds the new data to the dictionary
    full_db[(lat,lng)] = region
  return full_db


#Creates a dictionary of only the relevant long/lat : region pairs for the realisation
def getLocalDB(data_list, full_db):
  local_db = {}
  for data in data_list:
    if data[2] >= 0.00262:
      local_db[(data[0],data[1])] = full_db[(data[0],data[1])]
  return local_db


#Returns a list of the needed regions
def getRegions(local_db):
  regions = []
  for lat_lng in local_db:
    region = local_db[lat_lng]
    if region not in regions:
      regions.append(region)
  return regions


#Creates the dictionaries to hold probabilities for each region in each bin
#Takes in a list of the regions involved in the realisation
def binDicts(regions):
  vlow_regions = {}
  low_regions = {}
  mod_regions = {}
  high_regions = {}
  vhigh_regions = {}
  for i in range(len(regions)):
    vlow_regions[regions[i]] = []
    low_regions[regions[i]] = []
    mod_regions[regions[i]] = []
    high_regions[regions[i]] = []
    vhigh_regions[regions[i]] = []
  #Within each dictionary the region is the key and an empty list is the value
  return (vlow_regions, low_regions, mod_regions, high_regions, vhigh_regions)


#Takes in lists of the probabilities in each bin for a specific region. Returns lists with the 
#required umulative areas for the given region
def getRegionAreas(vlow, low, mod, high, vhigh, cell_area):
  #Total area effected within a certain region
  cumulat_area = (len(vlow) + len(low) + len(mod) + len(high) + len(vhigh)) * cell_area
  
  #Creates area lists for each bin and updates the cumulat_area for the next calculation
  (vlow_area, cumulat_area) = getArea(vlow, cumulat_area, cell_area)
  (low_area, cumulat_area) = getArea(low, cumulat_area, cell_area)
  (mod_area, cumulat_area) = getArea(mod, cumulat_area, cell_area)
  (high_area, cumulat_area) = getArea(high, cumulat_area, cell_area)
  (vhigh_area, cumulat_area) = getArea(vhigh, cumulat_area, cell_area)
  
  return (vlow_area, low_area, mod_area, high_area, vhigh_area)


#For a list of probabilities, a list is filled with cumulatative areas and returned
def getArea(bin, cumulat_area, cell_area):
  bin_area = []
  for prob in bin:
    cumulat_area -= cell_area
    bin_area.append(cumulat_area)
  return (bin_area, cumulat_area)
  
  
#Finds the two most impacted regions so they can be plotted
def getImpactedRegions(regions, vlow_area_regions):
  reg_area_impacted = []
  
  #For each region in the unique regions list
  for region in regions:
    #Adds the total area effected and the associated region to a list
    reg_area_impacted.append((max(vlow_area_regions[region]), region))
  
  #Sorts the list so that the regions with largest impacted area are at the end of the list
  reg_area_impacted.sort()
  
  return [reg_area_impacted[-1][1], reg_area_impacted[-2][1]]
  
  

#Variable to count the total number of zero points
zero_total = 0

#Lists to hold the total probabiliites in each bin
vlow_pts = []
low_pts = []
mod_pts = []
high_pts = []
vhigh_pts = []

#Lists to hold the total cumulative areas in each bin
vlow_area = []
low_area = []
mod_area = []
high_area = []
vhigh_area = []

#Colours for plotting each bin
colours = ['#008b00', '#ffd700', '#ff9c00', '#ff0000']

#Takes xyz file from the argument and turns it into a usable variable
parser = argparse.ArgumentParser()
parser.add_argument("xyz") #xyz file
args = parser.parse_args()
xyz = open(args.xyz)

#Dictionary of all region database data
full_db = getFullDB()

#Opens region_db for appending new entries
region_db = open('Region_database.txt', 'a')

#Gets data from xyz file
(data_list, prob_list, lat_lng) = getDataLists(xyz)

#Total number of grid points impacted by the realisation
total_pts = len(prob_list)

#Updates the full db and creates a local_db
print('Updating the database...')
for data in data_list:
  full_db = fillRegionDB(full_db, region_db, data[0], data[1], data[2])
print('Updated the database!')

#Creates a local db of the relevant lat/lngs and regions
local_db = getLocalDB(data_list, full_db)

#Gets a list of the unique regions impacted by the EQ
regions = getRegions(local_db)

#Each bin has a dictionary of region:empty list pairs
#The empty lists will be filled with probability values in the future
bins = binDicts(regions)
vlow_regions = bins[0]
low_regions = bins[1]
mod_regions = bins[2]
high_regions = bins[3]
vhigh_regions = bins[4]

#Gets the size of each cell and the total area of the grid
cell_area = getCellSize(lat_lng)
tot_area = cell_area * total_pts
cumulat_area = tot_area

#List of the lat/lng and prob values for all the non-zero probability points
non_zeroes = []

#Fills the non-zero list by filtering out zero prob points
for data in data_list:
  if data[2] < 0.00262:
    zero_total += 1
    cumulat_area -= cell_area
  else:
    non_zeroes.append((data[0], data[1], data[2]))

#Sorts the non-zero points by probability (low to high)
non_zeroes.sort(key=lambda a:a[2])

for point in non_zeroes:
  #Finds the region of the point
  region = local_db[(point[0],point[1])]
  
  #All points in the very low bin
  if point[2] < 0.05:
    #Adds the probability to the total list and the list for the specific region
    vlow_pts.append(point[2])
    vlow_regions[region].append(point[2])
    
    #Adds the cumulatative area to the total area list for the bin
    vlow_area.append(cumulat_area)
    
  #All points in low bin
  elif point[2] < 0.1:
    low_pts.append(point[2])
    low_regions[region].append(point[2])
    
    low_area.append(cumulat_area)
  
  elif point[2] < 0.2:
    mod_pts.append(point[2])
    mod_regions[region].append(point[2])
    
    mod_area.append(cumulat_area)
    
  elif point[2] < 0.4:
    high_pts.append(point[2])
    high_regions[region].append(point[2])
    
    high_area.append(cumulat_area)
    
  else:
    vhigh_pts.append(point[2])
    vhigh_regions[region].append(point[2])
    
    vhigh_area.append(cumulat_area)
  
  #Updates the total cumulatative area so that the lists fill up correctly
  cumulat_area -= cell_area

#Empty dictionaries which will link each region to a list of areas for plotting purposes
vlow_area_regions = {}
low_area_regions = {}
mod_area_regions = {}
high_area_regions = {}
vhigh_area_regions = {}

#For each region in the unique regions list 
for region in regions:
  #Fills the area dictionaries with cumulatative area lists
  (vlow_area_regions[region], low_area_regions[region], mod_area_regions[region], high_area_regions[region], vhigh_area_regions[region]) = getRegionAreas(vlow_regions[region], low_regions[region], mod_regions[region], high_regions[region], vhigh_regions[region], cell_area)


#Finds the two most impacted regions so they can be plotted
reg_to_plot = getImpactedRegions(regions, vlow_area_regions)

#Plotting:
fig = plt.figure()
gs = gridspec.GridSpec(2,2)

#Plots the total CCDF at the top of the plotting grid. Plot has different colours for risk areas
ax1 = fig.add_subplot(gs[0,:])
ax1.plot(vlow_area, vlow_pts, linewidth = 2, color = 'black')
ax1.plot(low_area, low_pts, linewidth = 2, color = colours[0])
ax1.plot(mod_area, mod_pts, linewidth = 2, color = colours[1])
ax1.plot(high_area, high_pts, linewidth = 2, color = colours[2])
ax1.plot(vhigh_area, vhigh_pts, linewidth = 2, color = colours[3])

#Adding a reference line
ref_area = 1760
ax1.axvline(x=ref_area, linestyle = '--')
ax1.text(ref_area + 200, 0.43, 'Stewart Island \n        Area \n (1760 Sq.Km)')

#Titles and labels for this ccdf
ax1.set_title('Total CCDF')
ax1.set_ylabel('Liquefaction Probability')
ax1.set_xlabel('Impacted Area (Sq.Km)')

#Plots on a logarithmic scale with certain bounds for x/y axes
ax1.set_xscale('log')
ax1.set_xlim((1, vlow_area[0]))
ax1.set_ylim((0,0.6))

#Removing ticks from the x-axis
ax1.xaxis.set_ticks_position('none')  


#Plotting a CCDF for the most impacted region
ax2 = fig.add_subplot(gs[1,0])
ax2.plot(vlow_area_regions[reg_to_plot[0]], vlow_regions[reg_to_plot[0]], linewidth = 2, color = 'black')
ax2.plot(low_area_regions[reg_to_plot[0]], low_regions[reg_to_plot[0]], linewidth = 2, color = colours[0])
ax2.plot(mod_area_regions[reg_to_plot[0]], mod_regions[reg_to_plot[0]], linewidth = 2, color = colours[1])
ax2.plot(high_area_regions[reg_to_plot[0]], high_regions[reg_to_plot[0]], linewidth = 2, color = colours[2])
ax2.plot(vhigh_area_regions[reg_to_plot[0]], vhigh_regions[reg_to_plot[0]], linewidth = 2, color = colours[3])

#Adds the same reference line on this CCDF for comparison
ax2.axvline(x=ref_area, linestyle = '--')
ax2.text(ref_area + 100, 0.43, '')

#Titles and labels
ax2.set_title('CCDF for ' + reg_to_plot[0] + ' Region')
ax2.set_ylabel('Liquefaction Probability')
ax2.set_xlabel(reg_to_plot[0] + ' Impacted Area (Sq.Km)')

#The axes have the same scale/bounds as the total ccdf to help with comparison
ax2.set_xscale('log')
ax2.set_ylim((0, 0.6))
ax2.set_xlim((1, vlow_area[0]))
ax2.xaxis.set_ticks_position('none') 


#Plotting a CCDF for the second most impacted region
ax3 = fig.add_subplot(gs[1,1])
ax3.plot(vlow_area_regions[reg_to_plot[1]], vlow_regions[reg_to_plot[1]], linewidth = 2, color = 'black')
ax3.plot(low_area_regions[reg_to_plot[1]], low_regions[reg_to_plot[1]], linewidth = 2, color = colours[0])
ax3.plot(mod_area_regions[reg_to_plot[1]], mod_regions[reg_to_plot[1]], linewidth = 2, color = colours[1])
ax3.plot(high_area_regions[reg_to_plot[1]], high_regions[reg_to_plot[1]], linewidth = 2, color = colours[2])
ax3.plot(vhigh_area_regions[reg_to_plot[1]], vhigh_regions[reg_to_plot[1]], linewidth = 2, color = colours[3])

#Adds reference line
ax3.axvline(x=ref_area, linestyle = '--')
ax3.text(ref_area + 100, 0.43, '')

#Titles and labels
ax3.set_title('CCDF for ' + reg_to_plot[1] + ' Region')
ax3.set_ylabel('Liquefaction Probability')
ax3.set_xlabel(reg_to_plot[1] + ' Impacted Area (Sq.Km)')

#Scale and bounds for the axes
ax3.set_xscale('log')
ax3.set_ylim((0,0.6))
ax3.set_xlim((1, vlow_area[0]))
ax3.xaxis.set_ticks_position('none') 


#Whitespace in the plotting grid
gs.update(wspace=0.5, hspace=0.5)

fig = plt.gcf()

#Saving ccdf to working directory
fig.savefig('CCDF with regional subplots.png')


#Prints percentage of points that are in each bin
print('\nTotal points: %d Zero points: %d' % (total_pts, zero_total))
print('Percentage of total points: \n')
print(" Very low:\t%.3f%%\n Low:\t\t%.3f%%\n Moderate:\t%.3f%%\n High:\t\t%.3f%%\n Very high:\t%.3f%%\n" % (len(vlow_pts) * 100.0 / total_pts, len(low_pts)* 100.0 / total_pts, len(mod_pts) * 100.0 / total_pts, len(high_pts) * 100.0 / total_pts, len(vhigh_pts) * 100.0 / total_pts))

#Prints total area that each bin holds
print('Area of each bin: \n')
print(" Very low:\t{:.3f} km^2\n Low:\t\t{:.3f} km^2\n Moderate:\t{:.3f} km^2\n High:\t\t{:.3f} km^2\n Very high:\t{:.3f} km^2\n" .format(len(vlow_pts) * cell_area, len(low_pts) * cell_area, len(mod_pts) * cell_area, len(high_pts) * cell_area, len(vhigh_pts) * cell_area))
