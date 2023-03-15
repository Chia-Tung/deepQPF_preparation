import os
import pathlib
import netCDF4 as nc
import numpy as np
from typing import List
from tqdm import tqdm
from datetime import datetime

from src.file_util import load_nc, save_nc


class Cropper:
    def __init__(
        self, 
        all_files: List[str], 
        lat_crop: List[float],
        lon_crop: List[float],
        key: str,
    ) -> None:
        self.orig_nc_files = all_files
        self.lat_crop = lat_crop
        self.lon_crop = lon_crop
        self.key = key
        self.check_dim()

    def check_dim(self):
        # get matrix attribute
        _, self.lat_array, self.lon_array = load_nc(self.orig_nc_files[0], self.key)
        self.input_shape = (len(self.lat_array), len(self.lon_array))
        print(f"Input latitude: {self.lat_array[0]} ~ {self.lat_array[-1]}")
        print(f"Input longitude: {self.lon_array[0]} ~ {self.lon_array[-1]}")
        print(f"Input shape: {self.input_shape}")
        
        # check target shape
        if (self.lat_crop[0] not in self.lat_array) | \
            (self.lat_crop[1] not in self.lat_array) | \
            (self.lon_crop[0] not in self.lon_array) | \
            (self.lon_crop[1] not in self.lon_array):
            raise RuntimeError(f"Invalid target shape.")
        
        # get target index
        self.iloc = []
        # np.where returns a shape like ([4, 0], [])
        self.iloc.append(np.where(self.lat_array == self.lat_crop[0])[0][0])
        self.iloc.append(np.where(self.lat_array == self.lat_crop[1])[0][0])
        self.iloc.append(np.where(self.lon_array == self.lon_crop[0])[0][0])
        self.iloc.append(np.where(self.lon_array == self.lon_crop[1])[0][0])
        self.output_shape = (self.iloc[1] - self.iloc[0] + 1, self.iloc[3] - self.iloc[2] + 1)
        print(f"Output latitude: {self.lat_array[self.iloc[0]]} ~ {self.lat_array[self.iloc[1]]}")
        print(f"Output longitude: {self.lon_array[self.iloc[2]]} ~ {self.lon_array[self.iloc[3]]}")
        print(f"Output shape: {self.output_shape}")

    def execute(
        self, 
        output_path: str,
        remove_old_files: bool = False
    ) -> None:
        for file in tqdm(self.orig_nc_files):
            # load
            data, lat, lon = load_nc(file, self.key)

            # check action
            if np.shape(data) != self.input_shape:
                raise RuntimeError(f"{os.path.basename(file)} has wrong-shaped input data.")

            # remove original files
            if remove_old_files:
                os.remove(file)

            # crop
            data = data[self.iloc[0]:self.iloc[1]+1, self.iloc[2]:self.iloc[3]+1]
            lat = lat[self.iloc[0]:self.iloc[1]+1] # lat: 720-160+1=561
            lon = lon[self.iloc[2]:self.iloc[3]+1] # lon: 680-240+1=441

            # save
            new_file_path = self.get_hierarchical_path_from_nc(file, output_path)
            save_nc(new_file_path, data, self.key, self.output_shape, 
                    self.lat_array[self.iloc[0]:self.iloc[1]+1], self.lon_array[self.iloc[2]:self.iloc[3]+1])

    def get_hierarchical_path_from_nc(
        self, 
        file_path: str, 
        output_path: str,
        file_format:str = "%Y%m%d_%H%M.nc"
    ):
        base_name = pathlib.Path(file_path).name
        dt = datetime.strptime(base_name.split('.')[0], "%Y%m%d_%H%M")
        return pathlib.Path(*[output_path, f"{dt.year}", f"{dt.year}{dt.month:02d}", 
             f"{dt.year}{dt.month:02d}{dt.day:02d}",dt.strftime(file_format)]
        )  