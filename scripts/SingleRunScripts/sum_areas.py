# This compiles all of the areas in the meshblock data from StatsNZ
# The data takes meshblock_area.csv and produces meshblock_area_compiled.csv

i_data = open('/home/lukelongworth/meshblock_area.csv')
f_data = open('/home/lukelongworth/meshblock_area_compiled.csv', 'a')

meshblock_p = '0000100'
area_t = 0

for line in i_data:
    data = line.split('\t')
    meshblock = str(data[0])
    area = float(data[1])

    if meshblock == meshblock_p:
        area_t += area
    else:
        f_data.write(meshblock_p+' '+str(area_t)+'\n')
        meshblock_p = meshblock
        area_t = area
