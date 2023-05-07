import os
import numpy as np
import time
import concurrent.futures
import argparse
import glob
from typing import List
from tqdm import tqdm
from pathlib import Path

from src.file_readers.netcdf_reader import NetcdfReader
from src.utils.time_util import TimeUtil


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
        self.freader = NetcdfReader()
        self.check_dim()

    def check_dim(self):
        # get matrix attribute
        self.lat_array = self.freader.read(self.orig_nc_files[0], 'lat')
        self.lon_array = self.freader.read(self.orig_nc_files[0], 'lon')
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

    def execute(self, output_path: str, remove_old_files: bool, num_workers:int) -> None:
        unprocess_file_queue = []
        output_file_names = []
        for filename in tqdm(self.orig_nc_files, desc='traverse files'):
            dt = TimeUtil.parse_filename_to_time(Path(filename))         
            new_file_path = TimeUtil.get_filename_from_time(Path(output_path), dt)

            # remove original files
            if remove_old_files and new_file_path.exists():
                new_file_path.unlink()

            if not new_file_path.exists():
                unprocess_file_queue.append(filename)
                output_file_names.append(new_file_path)

        # run
        start_time = time.time()
        with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
            list(tqdm(executor.map(self.crop_one, unprocess_file_queue, 
                output_file_names), total=len(unprocess_file_queue), desc='execution'))
        end_time = time.time()
        print(f"spend {(end_time - start_time)/60:.2f} minutes.")

    def crop_one(self, filename: str, output_file_name:Path):        
        # load
        data = self.freader.read(filename, self.key)

        # check shape
        if np.shape(data) != self.input_shape:
            raise RuntimeError(
                f"{os.path.basename(filename)} has wrong-shaped input data.")

        # crop
        data = data[self.iloc[0]: self.iloc[1] + 1, 
                    self.iloc[2]: self.iloc[3] + 1]
        lat = self.lat_array[self.iloc[0]: self.iloc[1] + 1]  # lat: 720-160+1=561
        lon = self.lon_array[self.iloc[2]: self.iloc[3] + 1]  # lon: 680-240+1=441

        # save
        self.freader.save(output_file_name, data, self.key, self.output_shape, 
                        lat, lon)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='python main_crop.py')
    parser.add_argument('input_netCDF_path', type=str, help='Source data directory. \
        Only suitable for netCDF files.')
    parser.add_argument('output_netCDF_path', type=str,
                        help='Output file directory')
    parser.add_argument('--latitude_crop', nargs=2, metavar=('lat_start', 'lat_end'), type=float,
                        required=True, help='The latitude of cropped data')
    parser.add_argument('--longitude_crop', nargs=2, metavar=('lon_start', 'lon_end'), type=float,
                        required=True, help='The longitude of cropped data')
    parser.add_argument('-k', '--key', type=str, required=True,
                        help='The key of the input data when open a netCDF4 file.')
    args = parser.parse_args()
    
    file_list = glob.glob(f"{args.input_netCDF_path}/**/*.nc", recursive=True)
    file_list = sorted(file_list)

    cropper = Cropper(file_list, args.latitude_crop, args.longitude_crop, 
                    key=args.key)
    cropper.execute(output_path=args.output_netCDF_path, remove_old_files=False, 
                    num_workers=4)