# SPDX-FileCopyrightText: 2026- European Centre for Medium-Range Weather Forecasts (ECMWF)
# SPDX-License-Identifier: Apache-2.0

import pandas as pd
from .config import Config
import xarray as xr
import earthkit.data as ekd
import numpy as np
import plotly.express as px
from plotly.colors import get_colorscale
from earthkit.hydro._readers import find_main_var
from .station_mapping import StationMapping


def get_grid_inputs(grid_config):
    ds = ekd.from_source(*grid_config.source).to_xarray()
    nc_variable = grid_config.variable if grid_config.variable is not None else find_main_var(ds, 2)
    if nc_variable not in ds.data_vars:
        raise ValueError(
            f"Variable '{nc_variable}' not found in dataset. Available data variables: {list(ds.data_vars)}."
        )
    metric_grid = ds[nc_variable].values

    coord_dict = grid_config.coords
    coord_x = coord_dict.x
    coord_y = coord_dict.y

    grid_area_y_coords, grid_area_x_coords = xr.broadcast(ds[coord_y], ds[coord_x])
    grid_area_y_coords = grid_area_y_coords.values.copy()
    grid_area_x_coords = grid_area_x_coords.values.copy()

    return metric_grid, grid_area_y_coords, grid_area_x_coords


def get_station_inputs(station_config):
    df = pd.read_csv(station_config.file)
    filters = station_config.filter
    if filters is not None:
        df = df.query(filters)
    coord_x = station_config.coords.x
    coord_y = station_config.coords.y

    station_x_coords = df[coord_x].values
    station_y_coords = df[coord_y].values
    station_metric = df[station_config.metric].values
    return station_metric, station_y_coords, station_x_coords, df


def apply_blacklist(blacklist_config, metric_grid, grid_area_y_coords, grid_area_x_coords):
    if blacklist_config is not None:
        ds = ekd.from_source(*blacklist_config.source).to_xarray()
        nc_variable = find_main_var(ds, 2)
        mask = ds[nc_variable].values
        metric_grid[mask] = np.nan

    return metric_grid, grid_area_y_coords, grid_area_x_coords


def outputs_to_df(df, i, j, area, c_i, c_j, c_area, errors, grid_area_y_coords, grid_area_x_coords, shape, filename):
    df["opt_i"] = i
    df["opt_j"] = j
    df["near_i"] = c_i
    df["near_j"] = c_j
    df["near_area"] = c_area
    df["opt_error"] = errors
    df["opt_area"] = area
    df["opt_y_coord"] = grid_area_y_coords[i, 0]
    df["opt_x_coord"] = grid_area_x_coords[0, j]
    df["opt_1d_index"] = j + shape[1] * i
    if filename is not None:
        df.to_csv(filename.file, index=False)
    return df


def light_zero_color(colorscale_name="Viridis", zero_color="rgba(0,0,0,0)"):
    base = get_colorscale(colorscale_name)
    n = len(base)
    scaled = [[i / (n - 1), color] for i, (_, color) in enumerate(base)]
    scaled[0] = [0.0, zero_color]
    return scaled


def generate_summary_plots(df, plot_config):
    if plot_config is None:
        return

    distance_plot_config = plot_config.distance
    if distance_plot_config is not None:
        df["grid_offset_i"] = df["opt_i"] - df["near_i"]
        df["grid_offset_j"] = df["opt_j"] - df["near_j"]
        custom_scale = light_zero_color("Viridis")
        fig = px.density_heatmap(
            df,
            x="grid_offset_i",
            y="grid_offset_j",
            marginal_x="histogram",
            marginal_y="histogram",
            color_continuous_scale=custom_scale,
        )
        fig.write_html(distance_plot_config.file)
        fig.show()

    error_plot_config = plot_config.error
    if error_plot_config is not None:
        fig = px.histogram(df, x="opt_error")
        fig.write_html(error_plot_config.file)
        fig.show()


def mapper(config_dict: dict):
    config = Config(**config_dict)

    metric_grid, grid_area_y_coords, grid_area_x_coords = get_grid_inputs(config.grid)

    station_metric, station_y_coords, station_x_coords, df = get_station_inputs(config.station)

    metric_grid, grid_area_y_coords, grid_area_x_coords = apply_blacklist(
        config.blacklist, metric_grid, grid_area_y_coords, grid_area_x_coords
    )
    mapping_outputs = StationMapping(config.parameters).conduct_mapping(
        station_y_coords, station_x_coords, grid_area_y_coords, grid_area_x_coords, station_metric, metric_grid
    )
    df = outputs_to_df(
        df,
        *mapping_outputs,
        grid_area_y_coords,
        grid_area_x_coords,
        shape=grid_area_y_coords.shape,
        filename=config.output,
    )

    generate_summary_plots(df, config.plot)

    return df
