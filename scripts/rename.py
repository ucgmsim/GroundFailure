'''
This code produces a csv file that takes an ugly, easy-to-use, official, hard-to-understand realisation description like JorKekNeed_HYP01-03_S1254 and associates it with three strings describing the fault name in layman's terms, the relative hypocentre and slip distribution.

It is automated in /home/nesi00213/groundfailure/scripts/rename_faults.sh

Usage and examples
python /path/to/script/rename.py 'name of realisation' 'name of run' /path/to/output/directory/
python /home/nesi00213/groundfailure/scripts/rename.py $realisation $runs $out_dir
python /home/nesi00213/groundfailure/scripts/rename.py AlpineF2K_HYP01-03_S1254 v17p9 /home/lukelongworth/

Written by Luke Longworth | luke.longworth.nz@gmail.com
'''

# Initialisation
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument('realisation')
parser.add_argument('run')
parser.add_argument('out_dir')
args = parser.parse_args()
realisation1 = args.realisation
run = args.run
out_dir = args.out_dir

realisation = realisation1.split('_')
# realisation = (AlpineF2K, HYP01-03, S1254)

f = open('/home/nesi00213/groundfailure/scripts/Data/Fault_Names.csv','r') # Requires nesi to be up to date at this stage
rename = f.read()
#print(rename)
renames = rename.split('\n')
#print(renames)
i = 0
for compar in renames:
  #print(i)
  renames[i] = compar.split(',')
  i += 1
  
#print(renames)

for compar in renames:
  if compar[0] == realisation[0]:
    realisation[0] = compar[1]
    break

hyp = (realisation[1])[3:5]
slip = (realisation[2])[1:5]
try:
  hyp = float(hyp)
except ValueError:
  sys.exit()

slip = float(slip)
realisation[1] = 'Hypocentre #%.0f' %hyp
realisation[2] = 'Slip pattern #%.0f' %slip

f = open(out_dir+'/name_'+run+'.log','a+')
realisation = f.write(realisation1+','+realisation[0]+','+realisation[1]+','+realisation[2]+'\n')