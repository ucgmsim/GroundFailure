import argparse
import os
from geopy import Point
from geopy import distance
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.font_manager import FontProperties

#Takes the path to the run and makes it a usable variable
parser = argparse.ArgumentParser()
parser.add_argument('realisation')
args = parser.parse_args()

#Run name
realisation_path = args.realisation.split('/')
run = realisation_path[-4]
realisation = realisation_path[-1]

#List of colours for plotting
colours = ['#ff0000', '#00ff00', '#0000ff', '#ff00ff']

#Creates the figure for plotting
fig = plt.figure()
gs = gridspec.GridSpec(1,1)
ax = fig.add_subplot(gs[0,0])

#Index for selecting the colour to plot each line
col_index = 0

model_list = ['_zhu_2016_coastal_probability_nz-specific-vs30.xyz', '_zhu_2016_coastal_probability_topo-based-vs30.xyz','_zhu_2016_general_probability_nz-specific-vs30.xyz', '_zhu_2016_general_probability_topo-based-vs30.xyz']


for model in model_list:
  #Opens the general probability xyz file for the specific realisation
  xyz_path = args.realisation + '/' + run + model
  xyz = open(xyz_path)
  
  i = 0
  lat_lng = []
  prob_list = []
  
  #Adds probability and lat/lng data for the realisation to lists
  for line in xyz:
    if i < 6:
      i += 1
    else:
      data = line.split(' ')
      prob = data[2]
      prob = prob.strip('\n')
      prob = float(prob)
      
      if prob > 0.00262:
        prob_list.append(prob)

      lat_lng.append((data[1],data[0]))
      
  #Sorts the probabilities from low to high
  prob_list.sort()
      
  #Finds the size of the grid cell for the realisation
  lat_lng.sort()
  corner1 = Point(lat_lng[0]) #lat,lng of first corner of first cell (upper LH)
  corner2 = Point(lat_lng[1]) #lat,lng of second corner of first cell (upper RH)
  lat_lng.sort(key=lambda a: (a[1], a[0])) #sorts by longitude rather than latitude
  corner3 = Point(lat_lng[1]) #lat,lng of third corner of first cell (lower LH)
  
  cell_width = distance.great_circle(corner1,corner2).km
  cell_height = distance.great_circle(corner1,corner3).km
  
  cell_area = cell_width * cell_height
  
  #Total area to consider
  cumulat_area = cell_area * len(prob_list)
  area_list = []
  
  #Adds areas in a parallel list to the probability list
  for i in range(len(prob_list)):
    area_list.append((cumulat_area))
    cumulat_area -= cell_area
  
  model = model.split('_')
  model_type = model[3] + ' model,' + model[-1][0:-9]
  
  #Plots the ccdf for the realisation on the same plot as the other ccdfs
  ax.plot(area_list, prob_list, color = colours[col_index], label = model_type)

  #Move onto next colour
  col_index += 1
  

#Titles and labels
ax.set_title('CCDFs for all models of ' + realisation)
ax.set_ylabel('Liquefaction probability')
ax.set_xlabel('Impacted Area (Sq.Km)')
  
  
#Plots on a logarithmic scale with certain bounds for x/y axes
ax.set_xscale('log')
ax.set_xlim((1, area_list[0]))
ax.set_ylim((0,0.6))

#Removing ticks from the x-axis
ax.xaxis.set_ticks_position('none')

#Font for the legend
fontP = FontProperties()
fontP.set_size('medium')

#Puts a legend in the lower left corner of the plot
ax.legend(loc='lower left', prop = fontP)

#Saving ccdf to working directory
fig.savefig('CCDF_multiple_runs.png')
  