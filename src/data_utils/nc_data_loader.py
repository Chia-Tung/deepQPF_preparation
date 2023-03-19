import netCDF4 as nc
import numpy as np
from pathlib import Path
from typing import Tuple, List, Union

from src.data_utils.data_loader import DataLoader

class Netcdf4DataLoader(DataLoader):
    def __init__(self, file_name: str) -> DataLoader:
        assert file_name[-3:] == ".nc", "Not A Regular NetCDF4 File."

        self.check_file_exist(file_name)
        self._container = nc.Dataset(file_name)

    def extract_data(
            self, 
            *variable_names: Union[List[str], str]
        ) -> List[np.ma.core.MaskedArray]:
        return_value = []
        for variable_name in variable_names:
            return_value.append(self._container[variable_name][:])
        return return_value
    
    def show_variables(self) -> None:
        if self._container is None:
            raise RuntimeError("NC Files hasn't been loaded yet.")
        
        print(self._container.variables.keys())

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

    f = nc.Dataset(fname, 'w', format = 'NETCDF4')
    f.createDimension('lat', output_shape[0])   
    f.createDimension('lon', output_shape[1])
    f.createVariable(vname, np.float32, ('lat', 'lon')) 
    f.createVariable('lat', np.float32, ('lat'))  
    f.createVariable('lon', np.float32, ('lon'))
    f.variables['lat'][:] = output_lat
    f.variables['lon'][:] = output_lon
    f.variables[vname][:] = np.ma.masked_array(data, mask=None)
    f.close()