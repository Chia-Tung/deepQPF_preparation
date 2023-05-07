import argparse
import time
import concurrent.futures
import numpy as np
from pathlib import Path
from tqdm import tqdm

from src.file_readers.netcdf_reader import NetcdfReader
from src.file_readers.jay_reader import JayReader
from src.utils.time_util import TimeUtil

class Compressor:
    def __init__(self, src: str, dst: str):
        self._src = Path(src)
        self._dst = Path(dst)
        self.input_reader = NetcdfReader()
        self.output_reader = JayReader()
        self._all_files = sorted(self._src.rglob("*.nc"))  # List[PosixPath]

        if not self._dst.exists():
            self._dst.mkdir(parents=True, exist_ok=True)

        print(f'[{self.__class__.__name__}] SRC:{self._src} DST:{self._dst}')

    def run(self, num_workers: int):

        start_time = time.time()
        with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
            list(tqdm(
                executor.map(self._run, self._all_files), 
                total=len(self._all_files), 
                desc='execution'
                ))
        end_time = time.time()
        print(f"spend {(end_time - start_time)/60:.2f} minutes.")
    
    def _run(self, filepath: Path):
        if 'radar' in str(filepath):
            key = 'cv'
        elif 'rain' in str(filepath):
            key = 'qperr'

        # load data
        data = self.input_reader.read(filepath, key)
        datetime = TimeUtil.parse_filename_to_time(filepath)

        # compress
        data = self.preprocess_data(data)

        # save
        output_filepath = TimeUtil.get_filename_from_time(
            self._dst, datetime, format=self.output_reader.FORMAT)
        self.output_reader.save(output_filepath, data)

    def preprocess_data(self, data: np.ndarray) -> np.ndarray:
        """
        Returns:
            compressed_data (np.ndarray): Shape of (3, N).
                The corresponding dimension is rows, cols and values.
        """
        d0, d1 = np.where(data > 0)
        sane_values = data[d0, d1]
        return np.vstack([d0, d1, sane_values])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='python main_compress.py')
    parser.add_argument('src', type=str, help='source directory.')
    parser.add_argument('dst', type=str, help='destination directory')
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()

    compresser = Compressor(args.src, args.dst)
    compresser.run(num_workers=args.workers)
