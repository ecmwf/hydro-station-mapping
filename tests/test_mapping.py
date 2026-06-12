from hydro_station_mapping import mapper
import pandas as pd

config = {
    "station": {
        "file": "stations.csv",
        "filter": "(StationLon >= 0) and (drainage_area_provided >= 0)",
        "coords": {
            "y": "StationLat",
            "x": "StationLon"
        },
        "metric": "drainage_area_provided"
    },
    "grid": {
        "source": ["file", "upstream_area.nc"],
        "coords": {
            "y": "lat",
            "x": "lon"
        }
    },
    # "blacklist": {
    #     "source": ["file", "mask.nc"]
    # },
    "parameters": {
        "max_search_distance": 5,
        "metric_error_func": "mape", #options are mse, mape, mspe, mae, zero, rmse
        "distance_error_func": "mse",
        "lambda": 0, # error = metric_error_func + lambda * distance_error_func
        "max_error": 0.2, # if error>max_error, just take nearest point since we have no idea
        "min_error": 0 # if error[closest_point] <= min_error, don't bother searching (this is good enough)
    },
    # "output": {
    #     "file": "mapped_stations.csv"
    # },
    # "plot": {
    #     "error": {
    #         "file": "hist.html"
    #     },
    #     "distance": {
    #         "file": "heatmap.html"
    #     }
    # }
}

def create_required_files():
    import pandas as pd
    import numpy as np
    import xarray as xr

    # Create stations.csv
    station_data = {
        "StationLat": [10, 20, 30],
        "StationLon": [100, 110, 120],
        "drainage_area_provided": [50, 150, 250]
    }
    df_stations = pd.DataFrame(station_data)
    df_stations.to_csv("stations.csv", index=False)

    # Create upstream_area.nc
    lat = np.arange(0, 40, 10)
    lon = np.arange(90, 130, 10)
    area_data = np.array([
        [40, 60, 80, 100],
        [140, 160, 180, 200],
        [240, 260, 280, 300],
        [340, 360, 380, 400]
    ])
    
    ds = xr.Dataset(
        {
            "upstream_area": (["lat", "lon"], area_data)
        },
        coords={
            "lat": lat,
            "lon": lon
        }
    )
    ds.to_netcdf("upstream_area.nc")


def test_mapping():
    create_required_files()
    df = mapper(config)
    expected_df = pd.DataFrame({
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
        "opt_x_coord": [0, 10, 20],
        "opt_y_coord": [90, 90, 90],
        "opt_1d_index": [0, 4, 8]
    })
    pd.testing.assert_frame_equal(df, expected_df)