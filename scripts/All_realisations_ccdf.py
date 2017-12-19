import argparse
import os
from geopy import Point
from geopy import distance
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.font_manager import FontProperties
import numpy as np

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


#Processing the arguments
parser = argparse.ArgumentParser()
parser.add_argument('path')
parser.add_argument('grey', nargs = '?', default = 'not_grey')
args = parser.parse_args()

#Determining colours for plotting
if args.grey == 'grey':
  colours = ['grey', 'grey', 'grey', 'grey', 'grey', 'grey']
  grey = True
else:
  if args.grey != 'not_grey':
    print('To have grey lines please add "grey" argument when calling this script.')
    print('Defaulting to coloured lines...')
  colours = ['#ff0000', '#ff9900', '#ffff00', '#00ff00', '#0000ff', '#ff00ff']
  grey = False
  
#Index for selecting the colour of each line
col_index = 0

#For calculating the upper limit of the x-axis
max_area = 0
  
#Dictionaries for storing all probabilities and areas 
prob_dict = {}
area_dict = {}

#Creates the figure for plotting
fig = plt.figure()
gs = gridspec.GridSpec(1,1)
ax = fig.add_subplot(gs[0,0])


#Finds the name of the run that will be plotted (e.g. AlpineF2K)
run_path = args.path.split('/')
run = run_path[-1]

#List of all realisations for the run
realisation_list = os.listdir(args.path + '/Impact/Liquefaction/')
num_realisations = len(realisation_list)

#Variable to make sure lat/lng list is only filled once
first = True

#All lat/lng points for the run (same for each realisation)
lat_lng = []


#Filling out probability lists for each realisation
for realisation in realisation_list:
  prob_dict[realisation] = []
  area_dict[realisation] = []

  #Opens the general probability xyz file for the realisation
  xyz_path = args.path + '/Impact/Liquefaction/' + realisation + '/' + run + '_zhu_2016_general_probability_nz-specific-vs30.xyz'
  xyz = open(xyz_path)
  
  i = 0
  
  #Adds probability and lat/lng data for the realisation to lists
  for line in xyz:
    if i < 6:
      i += 1
    else:
      data = line.split(' ')
      prob = data[2]
      prob = prob.strip('\n')
      prob = float(prob)
      
      #Ignores values not on land
      if prob > 0.00262:
        prob_dict[realisation].append(prob)
      if first:
        lat_lng.append((data[1],data[0]))
  
  #Prevents re-filling the lat/lng list
  first = False
  

#Gets area of a grid cell
cell_area = getCellSize(lat_lng)


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
    
    for realisation in prob_dict:
      average.append(prob_dict[realisation][i])
    mean = np.mean(average)
    std_dev = np.std(average,ddof = 1)
    
    average_prob.append(mean)
    upper.append(mean + std_dev)
    lower.append(mean - std_dev)
    
    #Adds each area to the area list
    area_list.append(cumulat_area)
    cumulat_area -= cell_area
  
  #Plotting a mean ccdf on the figure
  ax.plot(area_list, average_prob, color = 'black', linewidth = 2, zorder = 2)
  ax.plot(area_list, upper, color = 'purple', linewidth = 1, zorder = 2, linestyle = '--')
  ax.plot(area_list, lower, color = 'blue', linewidth = 1, zorder = 2, linestyle = '--')


#Plots lines for each realisation
for realisation in prob_dict:
  prob_dict[realisation].sort()
  
  cumulat_area = len(prob_dict[realisation]) * cell_area
  
  #Finds the upper limit for the x-axis
  if cumulat_area > max_area:
    max_area = cumulat_area
  
  #Adds areas to the area list for the realisation
  for i in range(len(prob_dict[realisation])):
    area_dict[realisation].append(cumulat_area)
    cumulat_area -= cell_area
  
  #Plots the ccdf for the realisation
  ax.plot(area_dict[realisation], prob_dict[realisation], color = colours[col_index], label = realisation, zorder = 1)
  
  #Moves to the next colour
  col_index += 1
    
    
#Titles and labels
ax.set_ylabel('Liquefaction probability')
ax.set_xlabel('Impacted Area (Sq.Km)')
  
#Plots the x-axis on a logarithmic scale
ax.set_xscale('log')
ax.set_xlim((1, max_area))
ax.set_ylim((0,0.6))

#Removing ticks from the x-axis
ax.xaxis.set_ticks_position('none')

#Setting title based on type of plot requested
if args.grey != 'grey':
  #Font for the legend
  fontP = FontProperties()
  fontP.set_size('medium')
  
  #Puts a legend in the lower left corner of the plot
  ax.legend(loc='lower left', prop = fontP)
  
  #Title if doing a colour plot
  ax.set_title('CCDF for all realisations of ' + run + ' (General model, nz-specific)')
  
  #Saving ccdf to the correct directory for the run
  #fig.savefig(args.path + '/Impact/Liquefaction/CCDF_For_All_Realisations.png')
  
else:
  #Title for a grey plot
  ax.set_title('CCDF for all Realisations of ' + run + ' with a Mean Line \n(General model, nz-specific)')
  
  #Saving ccdf to the correct directory for the run
  #fig.savefig(args.path + '/Impact/Liquefaction/Mean_CCDF_For_All_Realisations.png')
  
#Saving ccdf to working directory
fig.savefig('CCDF_multiple_runs.png')
