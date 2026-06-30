import pytest
import pandas as pd
from hydro_station_mapping import mapper


def create_required_files():
    import numpy as np
    import xarray as xr

    station_data = {"StationLat": [10, 20, 30], "StationLon": [100, 110, 120], "drainage_area_provided": [50, 150, 250]}
    df_stations = pd.DataFrame(station_data)
    df_stations.to_csv("stations.csv", index=False)

    lat = np.arange(0, 40, 10)
    lon = np.arange(90, 130, 10)
    area_data = np.array([[40, 60, 80, 100], [140, 160, 180, 200], [240, 260, 280, 300], [340, 360, 380, 400]])

    ds = xr.Dataset({"upstream_area": (["lat", "lon"], area_data)}, coords={"lat": lat, "lon": lon})
    ds.to_netcdf("upstream_area.nc")


_station_cfg = {
    "file": "stations.csv",
    "filter": "(StationLon >= 0) and (drainage_area_provided >= 0)",
    "coords": {"x": "StationLon", "y": "StationLat"},
    "metric": "drainage_area_provided",
}
_grid_cfg = {
    "source": ["file", "upstream_area.nc"],
    "coords": {"x": "lon", "y": "lat"},
}

config_msd5 = {
    "station": _station_cfg,
    "grid": _grid_cfg,
    "parameters": {
        "max_search_distance": 5,
        "metric_error_func": "mape",
        "distance_error_func": "mse",
        "lambda": 0,
        "max_error": 0.2,
        "min_error": 0,
    },
}

config_msd1 = {
    "station": _station_cfg,
    "grid": _grid_cfg,
    "parameters": {
        "max_search_distance": 1,
        "metric_error_func": "mape",
        "distance_error_func": "mse",
        "lambda": 0,
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
    "config,expected",
    [
        (config_msd5, expected_msd5),
        (config_msd1, expected_msd1),
    ],
)
def test_mapping(config, expected):
    create_required_files()
    df = mapper(config)
    pd.testing.assert_frame_equal(df, expected)
