# SPDX-FileCopyrightText: 2026- European Centre for Medium-Range Weather Forecasts (ECMWF)
# SPDX-License-Identifier: Apache-2.0

import numpy as np
import pytest
import pandas as pd
import xarray as xr
from hydro_station_mapping import mapper


@pytest.fixture
def stations_file(tmp_path):
    station_data = {"StationLat": [10, 20, 30], "StationLon": [100, 110, 120], "drainage_area_provided": [50, 150, 250]}
    df_stations = pd.DataFrame(station_data)
    stations_path = tmp_path / "stations.csv"
    df_stations.to_csv(stations_path, index=False)
    return stations_path


@pytest.fixture
def upstream_area_file(tmp_path):
    lat = np.arange(0, 40, 10)
    lon = np.arange(90, 130, 10)
    area_data = np.array([[40, 60, 80, 100], [140, 160, 180, 200], [240, 260, 280, 300], [340, 360, 380, 400]])

    ds = xr.Dataset({"upstream_area": (["lat", "lon"], area_data)}, coords={"lat": lat, "lon": lon})
    upstream_area_path = tmp_path / "upstream_area.nc"
    ds.to_netcdf(upstream_area_path)
    return upstream_area_path


def build_config(stations_file, upstream_area_file, max_search_distance, variable=None):
    grid = {
        "source": ["file", str(upstream_area_file)],
        "coords": {"x": "lon", "y": "lat"},
    }
    if variable is not None:
        grid["variable"] = variable
    return {
        "station": {
            "file": str(stations_file),
            "filter": "(StationLon >= 0) and (drainage_area_provided >= 0)",
            "coords": {"x": "StationLon", "y": "StationLat"},
            "metric": "drainage_area_provided",
        },
        "grid": grid,
        "parameters": {
            "max_search_distance": max_search_distance,
            "metric_error_func": "mape",
            "distance_error_func": "mse",
            "distance_error_weight": 0,
            "max_error": 0.2,
            "min_error": 0,
        },
    }


expected_msd5 = pd.DataFrame(
    {
        "StationLat": [10, 20, 30],
        "StationLon": [100, 110, 120],
        "drainage_area_provided": [50, 150, 250],
        "opt_i": [0, 1, 2],
        "opt_j": [0, 0, 0],
        "near_i": [1, 2, 3],
        "near_j": [1, 2, 3],
        "near_area": [160.0, 280.0, 400.0],
        "opt_error": [0.200000, 0.066667, 0.040000],
        "opt_area": [40.0, 140.0, 240.0],
        "opt_y_coord": [0, 10, 20],
        "opt_x_coord": [90, 90, 90],
        "opt_1d_index": [0, 4, 8],
    }
)

expected_msd1 = pd.DataFrame(
    {
        "StationLat": [10, 20, 30],
        "StationLon": [100, 110, 120],
        "drainage_area_provided": [50, 150, 250],
        "opt_i": [0, 1, 2],
        "opt_j": [0, 1, 2],
        "near_i": [1, 2, 3],
        "near_j": [1, 2, 3],
        "near_area": [160.0, 280.0, 400.0],
        "opt_error": [0.2, 10 / 150, 30 / 250],
        "opt_area": [40.0, 160.0, 280.0],
        "opt_y_coord": [0, 10, 20],
        "opt_x_coord": [90, 100, 110],
        "opt_1d_index": [0, 5, 10],
    }
)


@pytest.mark.parametrize(
    "max_search_distance,variable,expected",
    [
        (5, None, expected_msd5),
        (1, None, expected_msd1),
        (5, "upstream_area", expected_msd5),
    ],
)
def test_mapping(stations_file, upstream_area_file, max_search_distance, variable, expected):
    config = build_config(stations_file, upstream_area_file, max_search_distance, variable)
    df = mapper(config)
    pd.testing.assert_frame_equal(df, expected)
