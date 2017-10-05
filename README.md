# GroundFailure
Landslide and liquefaction calculations and plotting

This project runs on python 2.

It depends on https://github.com/usgs/groundfailure which runs on python 3. See their readme to see what dependancies this code has.

It requires a shakemap grid.xml (http://usgs.github.io/shakemap/) (and the models in this repository)

To run liquefaction

python /path/to/plot_liq.py /home/nesi00213/RealTime/*run_name*

To run landslide

python /path/to/plot_land.py /home/nesi00213/RealTime/*run_name*

The output files will be created in:
/path/to/runfolder/impact/(landslide|liquefaction)
