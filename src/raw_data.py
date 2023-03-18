import os
import numpy as np
from datetime import datetime
from netCDF4 import Dataset

import src.data_utils as du


class RawRadarData:
    def __init__(self, fpath: str):
        """
        Example fpath: 'RADARCV_2018/201809/20180908_1300.nc'
        """
        self._fpath = fpath

    def datetime(self):
        assert self._fpath[-3:] == '.nc', f"{self._fpath} gets unsupported format."
        dt_str = os.path.basename(self._fpath)[:-3]
        return datetime.strptime(dt_str, '%Y%m%d_%H%M')

    def load(self):
        assert os.path.exists(self._fpath), f'{self._fpath} does not exist!'
        data, lat, lon = du.Netcdf4DataLoader(self._fpath).extract_data('cv', 'lat', 'lon')
        return {'radar': np.array(data), 'lat': np.array(lat), 'lon': np.array(lon)}


class RawRainData:
    def __init__(self, fpath: str):
        """
        Example fpath: 'QPESUMS_rain_2018/201809/20180908_1300.nc'
        """
        self._fpath = fpath

    def datetime(self):
        assert self._fpath[-3:] == '.nc', self._fpath
        dt_str = os.path.basename(self._fpath)[:-3]
        return datetime.strptime(dt_str, '%Y%m%d_%H%M')

    def load(self):
        assert os.path.exists(self._fpath), f'{self._fpath} does not exist!'
        data, lat, lon = du.Netcdf4DataLoader(self._fpath).extract_data('qperr', 'lat', 'lon')
        return {'rain': np.array(data), 'lat': np.array(lat), 'lon': np.array(lon)}


class RawQpesumsData:
    def __init__(self, fpath: str):
        """
        Example fpath: '20180114_0650_f1hr.nc'
        """
        self._fpath = fpath

    def datetime(self):
        assert self._fpath[-3:] == '.nc', self._fpath
        dt_str = os.path.basename(self._fpath)[:-3]
        dt_str = '_'.join(dt_str.split('_')[:2])
        return datetime.strptime(dt_str, '%Y%m%d_%H%M')

    def load(self):
        assert os.path.exists(self._fpath), f'{self._fpath} does not exist!'
        data = Dataset(self._fpath, 'r')
        rr = data.variables['qpfrr'][:]
        return {'rain': np.array(rr), 'dt': self.datetime()}
