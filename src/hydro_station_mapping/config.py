# (C) Copyright 2026- ECMWF and individual contributors.

# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.

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


class BlackListConfig(BaseModel):
    source: List[str]


class MappingParametersConfig(BaseModel):
    max_search_distance: float = 5
    metric_error_func: Literal["zero", "mape", "mspe", "mae", "mse", "rmse"] = "mape"
    distance_error_func: Literal["zero", "mape", "mspe", "mae", "mse", "rmse"] = "zero"
    lambd: float = 0
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
