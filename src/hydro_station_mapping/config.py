# SPDX-FileCopyrightText: 2026- European Centre for Medium-Range Weather Forecasts (ECMWF)
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel

from typing import List, Literal
import numpy as np


class CoordsConfig(BaseModel):
    x: str = "lon"
    y: str = "lat"


class StationConfig(BaseModel):
    file: str
    coords: CoordsConfig = CoordsConfig()
    metric: str
    filter: str | None = None


class GridConfig(BaseModel):
    source: List[str]
    coords: CoordsConfig = CoordsConfig()
    variable: str | None = None


class BlackListConfig(BaseModel):
    source: List[str]


class MappingParametersConfig(BaseModel):
    max_search_distance: int = 5
    metric_error_func: Literal["zero", "mape", "mspe", "mae", "mse", "rmse"] = "mape"
    distance_error_func: Literal["zero", "mape", "mspe", "mae", "mse", "rmse"] = "zero"
    distance_error_weight: float = 0
    max_error: float = np.inf
    min_error: float = 0


class OutputConfig(BaseModel):
    file: str


class PlotConfig(BaseModel):
    error: OutputConfig | None = None
    distance: OutputConfig | None = None


class Config(BaseModel):
    station: StationConfig
    grid: GridConfig
    blacklist: BlackListConfig | None = None
    parameters: MappingParametersConfig = MappingParametersConfig()
    output: OutputConfig | None = None
    plot: PlotConfig | None = None
