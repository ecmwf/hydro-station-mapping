import numpy as np

from hydro_station_mapping import metrics


class StationMapping:
    def __init__(self, config):
        self.max_search_distance = config.get("max_search_distance", 5)
        self.metric_error_func = getattr(metrics, config.get("metric_error_func", "mape"))
        self.distance_error_func = getattr(metrics, config.get("distance_error_func", "no_error"))
        self.lambd = config.get("lambda", 0)
        self.max_error = config.get("max_error", np.inf)
        self.min_error = config.get("min_error", 0)

    def conduct_mapping(
        self,
        station_y_coords, station_x_coords, grid_area_y_coords, grid_area_x_coords,
        station_metric=None,
        grid_metric=None,
    ):

        num_stations = len(station_y_coords)

        i_arr = np.empty(num_stations, dtype=int)
        j_arr = np.empty(num_stations, dtype=int)
        c_i_arr = np.empty(num_stations, dtype=int)
        c_j_arr = np.empty(num_stations, dtype=int)
        errors = np.empty(num_stations, dtype=float)
        c_areas = np.empty(num_stations, dtype=float)
        best_areas = np.empty(num_stations, dtype=float)

        for s in range(num_stations):
            station_y, station_x = station_y_coords[s], station_x_coords[s]

            # get all grid cells within max_search_distance
            closest_i = np.nanargmin(np.abs(grid_area_y_coords[:, 0] - station_y))
            closest_j = np.nanargmin(np.abs(grid_area_x_coords[0, :] - station_x))

            searchbox_min_i = closest_i - self.max_search_distance
            searchbox_max_i = closest_i + self.max_search_distance + 1
            searchbox_min_j = closest_j - self.max_search_distance
            searchbox_max_j = closest_j + self.max_search_distance + 1
            # TODO: add option to wrap domain
            searchbox_min_i = max(0, searchbox_min_i)
            searchbox_max_i = min(grid_area_y_coords.shape[0], searchbox_max_i)
            searchbox_min_j = max(0, searchbox_min_j)
            searchbox_max_j = min(grid_area_y_coords.shape[1], searchbox_max_j)

            subset_y = grid_area_y_coords[searchbox_min_i:searchbox_max_i, searchbox_min_j:searchbox_max_j]
            subset_x = grid_area_x_coords[searchbox_min_i:searchbox_max_i, searchbox_min_j:searchbox_max_j]

            shape = subset_y.shape

            subset_y = subset_y.flatten()
            subset_x = subset_x.flatten()

            subset_coords = np.stack((subset_y, subset_x), axis=0)
            coords_vec = np.array([station_y, station_x])

            distance_error = self.distance_error_func(coords_vec, subset_coords)

            if station_metric is None:
                area_error = 0
            else:
                assert grid_metric is not None
                subset_metric = grid_metric[searchbox_min_i:searchbox_max_i, searchbox_min_j:searchbox_max_j].flatten()
                area_error = self.metric_error_func(station_metric[s], subset_metric)

            error = area_error + self.lambd * distance_error
            area = subset_metric

            try:
                best_error_1d_index = np.nanargmin(error)
                min_index = np.unravel_index(best_error_1d_index, shape)
                best_error = error[best_error_1d_index]
                best_area = area[best_error_1d_index]

                center_offset_i = closest_i - searchbox_min_i
                center_offset_j = closest_j - searchbox_min_j
                subset_width = searchbox_max_j - searchbox_min_j
                closest_1d_index = center_offset_i * subset_width + center_offset_j

                closest_error = error[closest_1d_index]
                closest_area = area[closest_1d_index]

                if closest_error <= self.min_error:  # if nearest cell is good enough
                    i = closest_i
                    j = closest_j
                    best_error = closest_error
                    best_area = closest_area
                elif best_error <= self.max_error:
                    i = (min_index[0] + searchbox_min_i) % grid_area_y_coords.shape[0]
                    j = (min_index[1] + searchbox_min_j) % grid_area_y_coords.shape[1]
                else:  # if best match is still too bad, revert to closest cell
                    i = closest_i
                    j = closest_j
                    best_error = closest_error
                    best_area = closest_area
            except ValueError:
                center_offset_i = closest_i - searchbox_min_i
                center_offset_j = closest_j - searchbox_min_j
                subset_width = searchbox_max_j - searchbox_min_j
                closest_1d_index = center_offset_i * subset_width + center_offset_j

                closest_error = error[closest_1d_index]
                closest_area = area[closest_1d_index]
                i = closest_i
                j = closest_j
                best_error = closest_error
                best_area = closest_area

            i_arr[s] = i
            j_arr[s] = j

            c_i_arr[s] = closest_i
            c_j_arr[s] = closest_j

            errors[s] = best_error
            best_areas[s] = best_area
            c_areas[s] = closest_area

        return i_arr, j_arr, best_areas, c_i_arr, c_j_arr, c_areas, errors
