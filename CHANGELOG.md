#
GroundFailure - Downstream hazard analysis. Liquefaction and Landslide
geospatial models

(Based on https://wiki.canterbury.ac.nz/download/attachments/58458136/CodeVersioning_v18p2.pdf?version=1&modificationDate=1519269238437&api=v2 )

## [Unreleased]
### Added
### Changed
### Fixed

## [19.5.1] - 2019-05-13
### Added
    - retrieve_vs30 gets the vs30 values on an interpolated grid with given lat/lon bounds and given grid step size

## [18.3.2] - 2017-04-06
### Changed
    - Updated CPT paths
    - Defaultly looking for gen_gf_surface in the same folder, making it more portable and able to run on other computers


## [18.3.1] - 2017-03-19 - Initial Release
### Fixed
    - Updated the plot_stations path
    - Updated some components of the hazard probability workflow
### Added
    - Commented grd2grid.py 
### Changed
    - Changed the default CPT for probability plots to hot-orange
