# (C) Copyright 2026- ECMWF and individual contributors.

# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.

import numpy as np


def metric_wrapper(func):
    def wrapper(val, grid):
        # prep grid
        if grid.ndim == 1:
            grid = grid[np.newaxis, :]  # (2,n) for dist, (1,n) for metric
        # prep val
        if np.isscalar(val):
            val = np.array([val])
        if val.ndim == 1:
            val = val[:, np.newaxis]  # (2,1) for dist, (1,1) for metric

        return func(val, grid)

    return wrapper


@metric_wrapper
def zero(val, grid):
    """
    Zero Error
    """
    return np.zeros(grid.shape[1:])


@metric_wrapper
def mape(val, grid):
    """
    Mean Absolute Percentage Error
    """
    denominator = np.where(np.abs(val) < 1e-8, 1e-8, np.abs(val))
    return np.mean(np.abs((val - grid) / denominator), axis=0)


@metric_wrapper
def mspe(val, grid):
    """
    Mean Absolute Percentage Error
    """
    denominator = np.where(np.abs(val) < 1e-8, 1e-8, np.abs(val))
    return np.mean(((val - grid) / denominator) ** 2, axis=0)


@metric_wrapper
def mae(val, grid):
    """
    Mean Absolute Error
    """
    return np.mean(np.abs(val - grid), axis=0)


@metric_wrapper
def mse(val, grid):
    """
    Mean Squared Error
    """
    return np.mean((val - grid) ** 2, axis=0)


@metric_wrapper
def rmse(val, grid):
    """
    Root Mean Squared Error
    """
    return np.sqrt(np.mean((val - grid) ** 2, axis=0))
