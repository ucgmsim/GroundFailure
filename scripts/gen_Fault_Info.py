from math import sin, cos, sqrt, atan2, radians
import os
import shlex

import argparse
parser = argparse.ArgumentParser(description='This is a PyMOTW sample program')
parser.add_argument('run')
parser.add_argument('out_dir')
args = parser.parse_args()

run = args.run
out_dir = args.out_dir

print(run)
print(out_dir)


NHM_START=15
NHM='NZ_FLTmodel_2010.txt'


def getmidcor(corners):
    #get the middle cooordinates
    distancetotal = []
    # print(len(corners))
    for plane in range(0, len(corners)):
        distance = []
        # print(corners[plane])
        for i in range(0, 4):
            lat1 = float(corners[plane][i][1])
            lon1 = float(corners[plane][i][0])
            if (i == 3):
                lat2 = float(corners[plane][0][1])
                lon2 = float(corners[plane][0][0])
            else:
                lat2 = float(corners[plane][i + 1][1])
                lon2 = float(corners[plane][i + 1][0])
            distance.append(getdis(lat1, lon1, lat2, lon2))
        distancetotal.append(distance)
        # print(distancetotal)

    midcor = []
    for i in range(0, len(distancetotal)):
        index = distancetotal[i].index(min(distancetotal[i]))
        if (index == 3):
            lat = (float(corners[i][index][1]) + float(corners[i][0][1])) / 2
            lon = (float(corners[i][index][0]) + float(corners[i][0][0])) / 2
            lat1 = (float(corners[i][1][1]) + float(corners[i][2][1])) / 2
            lon1 = (float(corners[i][1][0]) + float(corners[i][2][0])) / 2
        else:
            lat = (float(corners[i][index][1]) + float(corners[i][index + 1][1])) / 2
            lon = (float(corners[i][index][0]) + float(corners[i][index + 1][0])) / 2
            a = index + 2
            if a > 3:
                a = 0
                lat1 = (float(corners[i][index + 1][1]) + float(corners[i][a][1])) / 2
                lon1 = (float(corners[i][index + 1][0]) + float(corners[i][a][0])) / 2
            else:
                lat1 = (float(corners[i][index + 1][1]) + float(corners[i][a][1])) / 2
                lon1 = (float(corners[i][index + 1][0]) + float(corners[i][a][0])) / 2

        midcor.append((lat, lon, lat1, lon1))
    return midcor


def getdis(lat1,lon1,lat2,lon2):
    #calculate the distance
    R = 6373.0
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance


def getcorners(corner):
    #get corners data
    nuindex=0
    index_plane=[]
    plane_cord=[]

    for line in corner:
        #print(line)
        if 'plane' in line:
            index_plane.append(nuindex)
        nuindex = nuindex + 1
    for i in index_plane:
        cord=None
        cord_temp = []
        for ii in range (1,5):
            cord=corner[i+ii].split()
            #print(cord)
            cord_temp.append(cord)
        plane_cord.append(cord_temp)
    return(plane_cord)

def loadmsg(targets):
    msgs=None
    # loop through faults
    with open(NHM, 'r') as nf:
        db = nf.readlines()
    dbi = NHM_START
    dbl = len(db)
    while dbi < dbl:
        name = db[dbi].strip()
        n_pt = int(db[dbi + 11])
        if targets != None and name != targets:
            dbi += 13 + n_pt

            continue
        # retrieve required properties
        dip = float(db[dbi + 3].split()[0])
        dip_dir = float(db[dbi + 4])
        rake = float(db[dbi + 5])
        dbottom = float(db[dbi + 6].split()[0])
        dtop = float(db[dbi + 7].split()[0])
        mag = float(db[dbi + 10].split()[0])
        rcr_int = float(db[dbi + 10].split()[1])
        pts=[]
        #pts = list(map(float, ll.split()) for ll in db[dbi + 12: dbi + 12 + n_pt])
        for ll in db[dbi + 12: dbi + 12 + n_pt]:
            #print( )
            pts.append(list(map(float,ll.split())))
        # dictionary easy to retrieve, even with future changes
        msgs = {'name': name, 'dip': dip, 'dip_dir': dip_dir, 'rake': rake, \
                     'dbottom': dbottom, 'dtop': dtop, 'mag': mag, 'rcr_int': rcr_int, \
                     'n_pt': n_pt, 'points': pts}
        # next fault
        dbi += 13 + n_pt
    return msgs

def gencsv(names):
    #loop through names in the list
    for name in names:
        name = name.strip()
        msg = loadmsg(name)
        # print(msg)
        foldername = out_dir+'/website_data/'+run+'/'+name+'/realisation_list.txt'
        # print(foldername)
        f1=open((foldername),'r')
        namesf=f1.readlines()
        for name1 in namesf:
          name1 = name1.strip()
          fh = open(os.path.join(out_dir,'website_data',run,name,name1,name1+'-Faultinfo.csv'), 'w')
          fh1 = open(os.path.join(os.path.sep,'home','nesi00213','RunFolder','Cybershake',run,'Runs',name,'GM','Sim','Data',name,name1, 'corners.txt'), 'r')
        #fh1 = open(os.path.join(name, 'corners.txt'), 'r')
          corner = fh1.readlines()
        #print(corner)
          pt = corner[1]
          pt = ('(' + str(pt).strip() + ')')
        # print(msg['points'])
          fh.write(str(msg['mag']) + ',' + str(msg['dtop']) + ',' + pt + ',' + str(msg['rcr_int']))
          corners = getcorners(corner)
          midcor = getmidcor(corners)
          fh = open(os.path.join(out_dir,'website_data',run,name,name1,name1+'-Faultline.csv'), 'w')
          fh.write(',' + str(msg['name']) + ',' + str((midcor)))
    return()


f=open('/home/nesi00213/RunFolder/Cybershake/'+run+'/temp/list_runs_'+run,'r')
names=f.read()
names = names.split('\n')
# print(names)
gencsv(names)
print('done')












