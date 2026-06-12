Documentation
=============

.. important::

    This software is **Emerging** and subject to ECMWF's guidelines on `Software Maturity <https://github.com/ecmwf/codex/raw/refs/heads/main/Project%20Maturity>`_.

**hydro-station-mapping** is a Python package and commandline tool for conducting automatic mapping of station locations onto river networks.

Usage
-----

Either use the commandline utility by specifying a YAML configuration file::

   hydro-station-mapping config.yml

or the Python interface directly by passing a configuration dictionary::

   from hydro_station_mapping import mapper

   mapped_df = mapper(config)

Configuration
-------------

The configuration options are detailed below in YAML format::

   station:
      file: stations.csv # required, path to station file
      # any column names used below must exist in the station file
      metric: upstream_area # required, column name to use as metric for mapping
      filter: drainage_area_provided >= 10 # optional, filter to apply to station dataframe
      coords: # optional
         x: latitude # optional, default is lon
         y: longitude # optional, default is lat

   grid:
      source: ["file", "upstream_area.nc"] # required, earthkit-data from_source configuration to load upstream area grid. File must only have one main variable, namely the upstream area. Units must match the station file.
      coords: # optional
         x: latitude # optional, default is lon
         y: longitude # optional, default is lat

   parameters: # optional
      max_search_distance: 5 # optional, default is 5. Maximum search distance to consider grid cells as mapping candidates (Manhattan distance measured in number of gridcells from the station)
      metric_error_func: mape # optional, default is mape. Error function to compute metric error between station and grid cell
      distance_error_func: no_error # optional, default is zero (distance not considered). Error function to compute distance error between station and grid cell, using the coordinates specified above
      lambd: 0 # optional, default is 0. Weighting factor for distance error relative to metric error. Global error is computed as metric error + lambda * distance error
      max_error: inf # optional, default is np.inf. Maximum combined error (metric error + lambda * distance error) to consider a grid cell as a valid mapping candidate, otherwise the closest grid cell will be selected as the best candidate.
      min_error: 0 # optional, default is 0. If closest grid cell has a combined error (metric error + lambda * distance error) less than min_error, it will be selected as the best candidate without considering other grid cells, even if there are other grid cells with lower combined error.

   blacklist: # optional, default is no blacklist applied
      source: ["file", blacklist.csv] # earthkit-data from_source configuration to load blacklist boolean mask. Any blacklisted grid cells will be given nan values before mapping.

   output: # optional, default is no output saved
      file: mapped_stations.csv # path to save mapped station results as csv file

   plot: # optional, default is no plot
      error:
         file: hist.html # path to save interactive error plot figure
      distance:
         file: heatmap.html # path to save interactive distance error plot figure

For an example, see the notebooks folder.

Algorithm
---------

The mapping algorithm considers each station in turn and does the following:

1. compute the combined error (metric error + lambda * distance error) between the station and all grid cells within the max_search_distance box
2. if the closest gridcell (in terms of distance) has a combined error less than min_error, select it as the best candidate and skip searching other grid cells
3. if no considered gridcells have a combined error less than max_error, select the closest grid cell as the best candidate (even if blacklisted)
4. otherwise, select the grid cell with the lowest combined error as the best candidate
