import os, sys
import feather
import numpy as np
import pandas as pd
from datetime import datetime

from src.data_compressor import DataCompressor

class FeatherCompressor(DataCompressor):
    def __init__(self, *arg, **kwarg):
        super().__init__(*arg, **kwarg)

    def save(self, data: np.ndarray, dt: datetime, fname: str):
        fpath = self.target_path(dt, fname)
        sparse_data = self.preprocess_data(data)
        df = pd.DataFrame({
            'x': sparse_data[0],
            'y': sparse_data[1],
            'value': sparse_data[2]
        })
        feather.write_dataframe(df, fpath)

    def target_path(self, dt: datetime, fname: str):
        """
        fname = yyyymmdd_HHMM.nc
        """
        return os.path.join(
            self.ddir,
            str(dt.year),
            f'{dt.year}{dt.month:02}',
            f'{dt.year}{dt.month:02}{dt.day:02}',
            fname.replace('nc', 'feather')
        )
    
    def preprocess_data(self, data: np.ndarray):
        d0, d1 = np.where(data > 0)
        sane_values = data[d0, d1]
        return d0, d1, sane_values

