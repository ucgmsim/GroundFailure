#!/bin/bash

# For all the files ending in _grid.xml in the current directory run liquefaction and landslide to generate h5 files. The output directory is also the current directory

for grid in `ls *_grid.xml`
    do
    python3 /usr/bin/gfail zhu_2016_general_probability_nz-specific-vs30_19p1_100m.ini $grid --set-bounds 'zoom, pgv, 0' --hdf5 -o . -c /home/nesi00213/groundfailure/config/ -d /home/nesi00213/groundfailure/liquefaction_model
    python3 /usr/bin/gfail jessee_2017_probability.ini $grid --set-bounds 'zoom, pgv, 0' --hdf5 -o . -c /home/nesi00213/groundfailure/config/ -d /home/nesi00213/groundfailure/landslide_model
done
