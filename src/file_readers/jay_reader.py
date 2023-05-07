import pandas as pd
import numpy as np
import datatable as dtb
from pathlib import Path
from typing import List

from src.file_readers.basic_reader import BasicReader

class JayReader(BasicReader):
    INVALID_VALUE = -999.
    FORMAT = "%Y%m%d_%H%M.jay"

    def __init__(self):
        pass
    
    def read(
        self, 
        filename_list: List[str], 
        lat_array: np.ndarray, 
        lon_array: np.ndarray
    ) -> np.ndarray:
        # load data
        df_generator = dtb.iread(filename_list)
        # revert sparse matrix to 2D array
        array_data = []
        for df in df_generator:
            data = np.zeros([lat_array.size, lon_array.size], dtype=np.float32)
            data[df['lat_id'], df['lon_id']] = df['value']
            array_data.append(data[None])
        return np.concatenate(array_data, axis=0)

    def save(
        self, 
        oup_filename: Path, 
        data: np.ndarray,
    ):
        if not oup_filename.parent.exists():
            oup_filename.parent.mkdir(parents = True, exist_ok=True)

        data_dict = dict(
            lat_id = data[0],
            lon_id = data[1],
            value = data[2]
        )
        data_frame = dtb.Frame(pd.DataFrame(data_dict))
        data_frame['lat_id'] = dtb.int32 # convert data type
        data_frame['lon_id'] = dtb.int32
        data_frame['value'] = dtb.float32
        data_frame.to_jay(str(oup_filename))