import os
import numpy as np
import numpy.ma as ma
from netCDF4 import Dataset
from pathlib import Path
from typing import Tuple, List

def load_nc(file_path:str, vname: str) -> List[np.ndarray]:
    assert os.path.exists(file_path), f'{file_path} does not exist!'
    d = Dataset(file_path, 'r')
    data = d.variables[vname][:]
    data[np.where(data.mask!=0)] = -99
    data[data < 0] = 0
    lon = d.variables['lon'][:]
    lat = d.variables['lat'][:]
    return data, lat, lon

def save_nc(
    fname: str, 
    data: np.ndarray, 
    vname: str,
    output_shape: Tuple[int],
    output_lat: np.ndarray,
    output_lon: np.ndarray    
) -> None:
    if not Path(fname).parent.exists():
        Path(fname).parent.mkdir(parents = True, exist_ok=True)

    f = Dataset(fname, 'w', format = 'NETCDF4')
    f.createDimension('lat', output_shape[0])   
    f.createDimension('lon', output_shape[1])
    f.createVariable(vname, np.float32, ('lat', 'lon')) 
    f.createVariable('lat', np.float32, ('lat'))  
    f.createVariable('lon', np.float32, ('lon'))
    f.variables['lat'][:] = output_lat
    f.variables['lon'][:] = output_lon
    f.variables[vname][:] = ma.masked_array(data, mask=None)
    f.close()