import os
import argparse
import numpy as np
from pathlib import Path
from tqdm import tqdm
from datetime import timedelta
from typing import Tuple

import src.file_readers as freader
from src.utils.time_util import TimeUtil
from src.data_structures.fixed_size_array import FixedSizeArray


class Cleaver:
    def __init__(
        self,
        inp_dir: str,
        oup_dir: str,
        cwd_dir: str,
        vname: str, 
        slice_type: str,
        mask_fname: str,
        fixed_array_fname: str,
        tolerance: int = 12,
    ):
        """Split 1-h accumulated rainfall (mm) into 10-m rain rate (mm/h)
        Args:
            inp_dir (str): The input directory.
            oup_dir (str): The output directory.
            cwd_dir (str): Directory where `mask.json` and `fixed_size_array.json` store.
            vname (str): The data key name saved in the netCDF4 file.
            slice_type (str): 'last' or 'all'. Slice the last file in input directory or 
                all files.
            mask_fname (str): Customized name of `mask.json`.
            fixed_array_fname (str): Customized name of `fixed_size_array.json`.
            tolerance (int): Number of data waiting until saving the data.
        """
        self.inp_dir = Path(inp_dir)
        self.oup_dir = Path(oup_dir)
        self.cwd_dir = Path(cwd_dir)
        self.mask_path = self.cwd_dir/mask_fname
        self.fixed_size_array_path = self.cwd_dir/fixed_array_fname
        self.vname = vname
        self.tolr = tolerance
        self.build_variables()

        if slice_type == "last":
            raise RuntimeError(f"slice last frame is not implemented.")
        elif slice_type == "all":
            self.run = self.slice_all_fn

    def build_variables(self):
        self.all_files = sorted(self.inp_dir.rglob(f"**/*.nc"))
        self.file_reader = freader.NetcdfReader()
        self.lat = self.file_reader.read(self.all_files[0], 'lat')
        self.lon = self.file_reader.read(self.all_files[0], 'lon')

    def slice_all_fn(self):
        """
        NOTE: `slice_all_fn` won't save the `mask.json` and `fixedSizeArray.json`. 
        """
        mask = None
        fix_sized_array = None

        for filename in tqdm(self.all_files):
            mask, fix_sized_array, output_fname = \
                self._slice_single_fn(filename, mask, fix_sized_array)
            
            if fix_sized_array.cnt >= self.tolr:
                # save first one in unit mm/hr
                first_data = fix_sized_array.data[0]
                self.file_reader.save(output_fname, first_data, self.vname, \
                    first_data.shape, self.lat, self.lon)

    def _slice_single_fn(
            self, 
            curr_fname: Path,
            mask: np.ndarray, 
            fix_sized_array: FixedSizeArray
        ) -> Tuple[np.ndarray, FixedSizeArray, Path]:
        """
        Args:
            curr_fname (Path): Current netCDF4 filename.
            mask (np.ndarray): The old mask produced by previous data.
            fix_sized_array (FixedSizeArray): Data container contains previous 6 frames.
        Return:
            new_mask (np.ndarray): The new mask produced by current data.
            fix_sized_array (FixedSizeArray): Data container contains previous 6 frames, 
                including the current data.
            output_filename (Path): The absolute path to save the t-50min data.
        """
        curr_time = TimeUtil.parse_filename_to_time(curr_fname)
        curr_data = self.file_reader.read(curr_fname, self.vname)
        prev_time = curr_time - timedelta(minutes=10)
        prev_fname = TimeUtil.get_filename_from_time(self.inp_dir, prev_time)

        # check if output file exists
        output_dt = curr_time - timedelta(minutes=50)
        output_fname = TimeUtil.get_filename_from_time(self.oup_dir, output_dt)
        assert not output_fname.exists(), f'{curr_fname.name} doesn\'t have next file.'
        
        # 10-m previous data doesn't exists
        if not prev_fname.exists():
            mask = (curr_data == 0) * 1
            fix_sized_array = FixedSizeArray()
            fix_sized_array.fit_mask(mask)
            print(f'No previous data for splitting, first init {curr_fname.name}.')
            return mask, fix_sized_array, output_fname
        
        # step 1. (data - sum(fix_sized_array[1:6]) * mask
        data_increment = (curr_data - fix_sized_array.five_sum()) * mask
        data_increment[data_increment < 0] = 0

        # step 2. push into fix_sized_array[6], and pop fix_sized_array[0] 
        fix_sized_array.append(data_increment)

        # step 3. find data == 0
        mask_new = (curr_data == 0) * 1

        # step 4. clean fix_sized_array
        fix_sized_array.fit_mask(mask_new)

        # step 5. update mask
        mask = np.where(mask + mask_new >= 1, 1, 0)

        return mask, fix_sized_array, output_fname

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path", type=str, help="enter input data path")
    parser.add_argument("output_path", type=str, help="enter output data path")
    parser.add_argument("vname", type=str, help="the variable name saved in the netCDF4 file")
    parser.add_argument("-c", "--current_path", type=str, default=os.getcwd(),
        help="current working directory stores the mask.json and fixed_size_array.json")
    parser.add_argument("--type", choices=["last", "all"], default="all", 
        help="want to slice the last frame or all of the data")
    args = parser.parse_args()

    inp_dir = args.input_path
    oup_dir = args.output_path
    cwd_dir = args.current_path
    vname = args.vname
    slice_type = args.type
    mask_fname = 'mask.json'
    fixed_array_fname = 'fixedSizeArray.json'

    rain_cleaver = Cleaver(
        inp_dir, oup_dir, cwd_dir, vname, slice_type, mask_fname, fixed_array_fname
    ).run()