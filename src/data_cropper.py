import os
import pathlib
import numpy as np
import time
import concurrent.futures
from itertools import repeat
from typing import List
from tqdm import tqdm
from datetime import datetime

from src.data_util import load_nc, save_nc


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
        _, self.lat_array, self.lon_array = load_nc(
            self.orig_nc_files[0], self.key)
        self.input_shape = (len(self.lat_array), len(self.lon_array))
        print(f"Input latitude: {self.lat_array[0]} ~ {self.lat_array[-1]}")
        print(f"Input longitude: {self.lon_array[0]} ~ {self.lon_array[-1]}")
        print(f"Input shape: {self.input_shape}")

        # check target shape
        if (
            (self.lat_crop[0] not in self.lat_array)
            | (self.lat_crop[1] not in self.lat_array)
            | (self.lon_crop[0] not in self.lon_array)
            | (self.lon_crop[1] not in self.lon_array)
        ):
            raise RuntimeError(f"Invalid target shape.")

        # get target index
        self.iloc = []
        # np.where returns a shape like ([4, 0], [])
        self.iloc.append(np.where(self.lat_array == self.lat_crop[0])[0][0])
        self.iloc.append(np.where(self.lat_array == self.lat_crop[1])[0][0])
        self.iloc.append(np.where(self.lon_array == self.lon_crop[0])[0][0])
        self.iloc.append(np.where(self.lon_array == self.lon_crop[1])[0][0])
        self.output_shape = (
            self.iloc[1] - self.iloc[0] + 1,
            self.iloc[3] - self.iloc[2] + 1,
        )
        print(
            f"Output latitude: {self.lat_array[self.iloc[0]]} ~ {self.lat_array[self.iloc[1]]}"
        )
        print(
            f"Output longitude: {self.lon_array[self.iloc[2]]} ~ {self.lon_array[self.iloc[3]]}"
        )
        print(f"Output shape: {self.output_shape}")

    def execute(self, output_path, remove_old_files, max_workers) -> None:
        start_time = time.time()
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=max_workers
        ) as executor:
            list(
                tqdm(
                    executor.map(
                        self.crop_one,
                        self.orig_nc_files,
                        repeat(output_path),
                        repeat(remove_old_files),
                    ),
                    total=len(self.orig_nc_files),
                )
            )
        end_time = time.time()
        print(f"spend {end_time - start_time} seconds.")

    def crop_one(self, file, output_path, remove_old_files):
        # load
        data, lat, lon = load_nc(file, self.key)

        # check action
        if np.shape(data) != self.input_shape:
            raise RuntimeError(
                f"{os.path.basename(file)} has wrong-shaped input data.")

        # remove original files
        if remove_old_files:
            os.remove(file)

        # crop
        data = data[self.iloc[0]: self.iloc[1] +
                    1, self.iloc[2]: self.iloc[3] + 1]
        lat = lat[self.iloc[0]: self.iloc[1] + 1]  # lat: 720-160+1=561
        lon = lon[self.iloc[2]: self.iloc[3] + 1]  # lon: 680-240+1=441

        # save
        new_file_path = self.get_hierarchical_path_from_nc(file, output_path)
        if new_file_path.exists():
            return
        save_nc(
            new_file_path,
            data,
            self.key,
            self.output_shape,
            self.lat_array[self.iloc[0]: self.iloc[1] + 1],
            self.lon_array[self.iloc[2]: self.iloc[3] + 1],
        )

    def get_hierarchical_path_from_nc(
        self, file_path: str, output_path: str, file_format: str = "%Y%m%d_%H%M.nc"
    ) -> pathlib.Path:
        base_name = pathlib.Path(file_path).name
        dt = datetime.strptime(base_name.split(".")[0], "%Y%m%d_%H%M")
        return pathlib.Path(
            *[
                output_path,
                f"{dt.year}",
                f"{dt.year}{dt.month:02d}",
                f"{dt.year}{dt.month:02d}{dt.day:02d}",
                dt.strftime(file_format),
            ]
        )
