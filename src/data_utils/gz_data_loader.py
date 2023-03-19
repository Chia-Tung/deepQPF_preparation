import numpy as np
from typing import List

from src.data_utils.data_loader import DataLoader


class GzipDataLoader(DataLoader):
    def __init__(self, file_name: str) -> DataLoader:
        assert file_name[-3:] == ".gz", "Not A Regular Gzip File."

        self.check_file_exist(file_name)
        self._container = np.loadtxt(file_name, dtype=np.float32)

    def extract_data(
        self,
        NY: int,
        NX: int,
    ) -> List[np.ma.core.MaskedArray]:
        return_value = np.zeros([NY, NX])
        return_value[self._container[0, :].astype(np.int8), 
                     self._container[1, :].astype(np.int8)] = self._container[2, :]
        return return_value
