'''
NOT TESTED!!!
This has been tested for runs on Hypocentre
Requires: xyz file of long/lat and proability data

This script takes the xyz file and uses the information to plot probability
against cumulative area on a ccdf. x-axis is logarithmically scaled. There is 
a reference line for the area of Stewart Island. Works for both landslide and liquefaction 
probability data.

Usage: Multiple_runs_ccdf.py "Path to xyz file"

Writes a png of the ccdf to current working directory.

@date 13 Dec 2017
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
from matplotlib.font_manager import FontProperties


j = 0
max_area = 0
colours = ['#008b00', '#ffd700', '#ff9c00', '#ff0000']
styles = ['solid', 'dashed', 'dashdot', 'dotted']

parser = argparse.ArgumentParser()
parser.add_argument('-l','--list', nargs='+', help='<Required> Set flag', required=True)
args = parser.parse_args()

#Plotting ccdf with the line as several different colours for the different risk levels
fig = plt.figure()
gs = gridspec.GridSpec(1,1)

#Plots the total CCDF at the top of the plotting grid. Plot has different colours for risk areas
ax = fig.add_subplot(gs[0,0])

for realisation_path in args._get_kwargs()[0][1]:
  xyz = open(realisation_path)
  
  realisation = realisation_path.split('/')[-2]
  
  i = 0
  prob_list = []
  lat_lng = []
  
  for line in xyz:
    if i < 6:
      i += 1
    else:
      data = line.split(' ')
      prob = data[2]
      prob = prob.strip('\n')
      prob_list.append(float(prob))
      lat_lng.append((data[1],data[0]))
      
  zero = 0

  #Lists to hold probabiliites in each bin
  vlow_prob = []
  low_prob = []
  mod_prob = []
  high_prob = []
  vhigh_prob = []
  total_prob = []
  
  #Lists to hold the cumulative areas in each bin
  vlow_area = []
  low_area = []
  mod_area = []
  high_area = []
  vhigh_area = []
  total_area = []
        
  prob_list.sort()
  total_pts = float(len(prob_list))
  
  #Grid details
  lat_lng.sort()
  corner1 = Point(lat_lng[0]) #lat,lng of first corner of first cell (upper LH)
  corner2 = Point(lat_lng[1]) #lat,lng of second corner of first cell (upper RH)
  lat_lng.sort(key=lambda a: (a[1], a[0])) #sorts by longitude rather than latitude
  corner3 = Point(lat_lng[1]) #lat,lng of third corner of first cell (lower LH)
  
  cell_width = distance.great_circle(corner1,corner2).km
  cell_height = distance.great_circle(corner1,corner3).km
  
  #Areas in km^2
  cell_area = cell_width * cell_height
  tot_area = cell_area * total_pts
  cumulat_area = tot_area
  
  for prob in prob_list:
    #Counts points in each bin and creates lists of probabilities and cumulative areas in each bin
    #Note that areas are plotted logarithmically
    if prob <= 0.00262 or math.isnan(prob):
      zero += 1
    elif prob < 0.05:
      vlow_prob.append(prob)
      vlow_area.append(cumulat_area)
    elif prob < 0.1:
      low_prob.append(prob)
      low_area.append(cumulat_area)
    elif prob < 0.2:
      mod_prob.append(prob)
      mod_area.append(cumulat_area)
    elif prob < 0.4:
      high_prob.append(prob)
      high_area.append(cumulat_area)
    else:
      vhigh_prob.append(prob)
      vhigh_area.append(cumulat_area)
    total_prob.append(prob)
    total_area.append(cumulat_area)
    
    #Adds probabilites to the y-pts and cumulative area to the x-pts
    cumulat_area -= cell_area
  
  #Plots the total CCDF at the top of the plotting grid. Plot has different colours for risk areas
  #plt.plot(total_area_dict[realisation], total_prob_dict[realisation], linewidth = 6, color = border[j], alpha = 0.75)
  
  ax.plot(vlow_area, vlow_prob, linewidth = 2, color = 'black', ls = styles[j], label = realisation)
  ax.plot(low_area, low_prob, linewidth = 2, color = colours[0], ls = styles[j])
  ax.plot(mod_area, mod_prob, linewidth = 2, color = colours[1], ls = styles[j])
  ax.plot(high_area, high_prob, linewidth = 2, color = colours[2], ls = styles[j])
  ax.plot(vhigh_area, vhigh_prob, linewidth = 2, color = colours[3], ls = styles[j])

  j += 1
  
  #find max area
  if vlow_area[0] > max_area:
    max_area = vlow_area[0]
  

#Adding a reference line
ref_area = 1760
ax.axvline(x=ref_area, linestyle = '--')
ax.text(ref_area + 200, 0.43, 'Stewart Island \n        Area \n (1760 Sq.Km)')

#Titles and labels for this ccdf
ax.set_title('CCDF for multiple realisations')
ax.set_ylabel('Liquefaction probability')
ax.set_xlabel('Impacted Area (Sq.Km)')
  
  
#Plots on a logarithmic scale with certain bounds for x/y axes
ax.set_xscale('log')
ax.set_xlim((1, max_area))
ax.set_ylim((0,0.6))

#Removing ticks from the x-axis
ax.xaxis.set_ticks_position('none')

fontP = FontProperties()
fontP.set_size('small')

# Put a legend to the right of the current axis
ax.legend(loc='lower left', prop = fontP)

#Saving ccdf to working directory
fig.savefig('CCDF_multiple_runs.png')
  