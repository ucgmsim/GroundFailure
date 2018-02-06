"""
Created: 19 January 2018
Purpose: Output "lat lng area data" is used to make CCDFs.
Author: Nicole Steinke <nst44@uclive.ac.nz>

USAGE:
Execute with python: "python2 get_point_area_data.py path/to/xyzfile path/to/shapefile path/to/datafile path/to/outfile"
First parameter: xyzfile, an be found in RunFolder on hypocentre.
Second parameter: shapefile, contains the meshblock data, use MB2013_GV_Clipped.
Third parameter: csvfile, contains meshblock code and data vaule e.g. population.
Fourth parameter: outfile, txt file where lat lng area data is to be stored.

NOTE:
Indices of shapefile has been set for MB2013_GV_Clipped.shp, where land area has index 25
To view index and fields of shapefile uncomment print statment on line 83.
"""

import ogr
import sys
import os

def get_point_area_data(xyzfile, shapefile, csvfile, outfile):
    """For longitude latitude point in xyzfile not in outfile
    checks which meshblock it is inside, and appends lat lng area data."""
    point_dict = {} # key: transformed point; value: lat/lng point
    data_dict = {} # key: meshblock code; value: data e.g. population
    point_set = set() # set, store points to check if in meshblock
    
    
    # Open xyz file and store longitude/latitude
    with open(xyzfile, 'r') as xyz:
        # first 6 lines contain header
        head = [next(xyz) for x in xrange(6)]
        for line in xyz:
            lng, lat, _ = line.strip().split(' ')
            point_set.add((lat,lng))

    
    # Remove points already in outfile from points_set
    if os.path.exists(outfile):
        with open(outfile, 'r') as f:
            for line in f:
                lat, lng, _, _ = line.split(" ")
                point_set.discard((lat,lng))
        out = open(outfile, 'a')
    else:
        out = open(outfile, 'w')
    
    if len(point_set) == 0:
        sys.exit(1)
    
    # Gets the data e.g. population, from the given csvfile
    with open(csvfile) as csv:
        for line in csv:
            code, data = line.strip('\n').split(',')
            
            # when confidental, use 0
            if data == "..C":
                data = 0
            else:
                data = int(data)
            
            if data_dict.get(code) == None:
                data_dict[code] = data
    
    
    # Open shapefile
    driver = ogr.GetDriverByName('ESRI Shapefile')
    dataSource = driver.Open(shapefile, 0)
    if dataSource is None:
        print 'Could not open shapefile'
        sys.exit(1)
    
    layer = dataSource.GetLayer(0)
    
    
    # Get feature fields
    schema = []
    ldefn = layer.GetLayerDefn()
    for n in range(ldefn.GetFieldCount()):
        fdefn = ldefn.GetFieldDefn(n)
        schema.append(fdefn.name)
        #print n, fdef.name
    
    
    # Setup transformation
    geo_ref = layer.GetSpatialRef()
    point_ref = ogr.osr.SpatialReference()
    point_ref.ImportFromEPSG(4326)
    ctran = ogr.osr.CoordinateTransformation(point_ref,geo_ref)

    # Transform lat/lng
    for point in point_set:
        lat = point[0]
        lng = point[1]
        [x,y,z]=ctran.TransformPoint(float(lng),float(lat))
        point = ogr.Geometry(ogr.wkbPoint)
        point.SetPoint_2D(0, x, y)
        point_dict[point] = (lat,lng)
    
    feat = layer.GetFeature(0)
    
    
    # Loop through the points in point_dict
    # Use spatial filter with each point so that the only features we see when we
    # loop through "layer" are those which overlap the current point
    for point, coord in point_dict.iteritems():
        layer.SetSpatialFilter(point)
        for feat in layer:
            geom = feat.GetGeometryRef()
            # for MB2013 shapefile: 0-area code,  25-land area, 26-shape leng, 27-shape area
            # indices  1-24 are other area codes and their name
            code = feat.GetField(schema[0])
            area = feat.GetField(schema[25])
            data = data_dict.get(code, 0)
            if point.Within(geom):
                out.write('{} {} {} {}\n'.format(coord[0],coord[1],area,data))
            feat.Destroy()
        layer.SetSpatialFilter(None)
    dataSource.Destroy()
    out.close()

if __name__ == "__main__":
    if len(sys.argv) == 5:
        get_point_area_data(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
    else:
        print "Require 4 arguments: xyzfile shapefile datafile outfile"
        sys.exit(1)
