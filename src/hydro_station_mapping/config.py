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
    min_error: float = 0 # if error[closest_point] <= min_error, don't bother searching (this is good enough)

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