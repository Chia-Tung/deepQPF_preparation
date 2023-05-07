import netCDF4 as nc
import numpy as np
from pathlib import Path
from typing import Tuple

from src.file_readers.basic_reader import BasicReader

class NetcdfReader(BasicReader):
    INVALID_VALUE = -999.
    FORMAT = "%Y%m%d_%H%M.nc"

    def __init__(self):
        pass
    
    def read(self, filename: Path, variable_name: str) -> np.ndarray:
        self.check_file_exist(str(filename))
        # load data
        mask_data = nc.Dataset(filename)[variable_name][:]
        # handle ma.MaskArray
        mask_data[mask_data.mask != 0] = self.INVALID_VALUE
        # convert to np.ndarray
        array_data = np.array(mask_data)
        return array_data
    
    def show_keys(self, filename: Path) -> None:
        self.check_file_exist(str(filename))
        print(nc.Dataset(filename).variables.keys())

    def save(
        self, 
        oup_filename: Path, 
        data: np.ndarray, 
        vname: str,
        shape: Tuple[int], 
        lat: np.ndarray, 
        lon: np.ndarray
    ):
        if not oup_filename.parent.exists():
            oup_filename.parent.mkdir(parents = True, exist_ok=True)

        f = nc.Dataset(oup_filename, 'w', format = 'NETCDF4')
        f.createDimension('lat', shape[0])   
        f.createDimension('lon', shape[1])
        f.createVariable(vname, np.float32, ('lat', 'lon')) 
        f.createVariable('lat', np.float32, ('lat'))  
        f.createVariable('lon', np.float32, ('lon'))
        f.variables['lat'][:] = lat
        f.variables['lon'][:] = lon
        f.variables[vname][:] = np.ma.masked_array(data, mask=None)
        f.close()