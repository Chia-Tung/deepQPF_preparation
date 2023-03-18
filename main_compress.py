import argparse
import os
import numpy as np
from datetime import datetime
from multiprocessing import Pool
from pathlib import Path
from tqdm import tqdm

from src.raw_data import RawRainData, RawRadarData


class DataCompressor:
    def __init__(
        self,
        source_dir: str,
        destination_dir: str,
        overwrite: bool,
    ) -> None:
        # overwirte: If True, replace the older files.
        self.sdir = Path(source_dir)
        self.ddir = Path(destination_dir)
        self.overwrite = overwrite
        if not self.ddir.exists():
            self.ddir.mkdir(parents=True, exist_ok=True)
        print(
            f'[{self.__class__.__name__}] SRC:{self.sdir} DST:{self.ddir} Overwrite:{self.overwrite}')

    def run(self, workers: int = 1):
        files = sorted(self.sdir.rglob("*.nc"))  # List[PosixPath]
        files = [(file,) for file in files] # multiprocess need arg iterable
        """
        The combination of tqdm and chunksize here is just a workaround.
        Not good enough.
        """
        with Pool(processes=workers) as pool:
            pool.starmap(self._compress, tqdm(files, total=len(files)), chunksize=10)

    def _compress(self, fname: Path):
        input_fpath = str(fname)

        if 'radar' in input_fpath:
            loader = RawRadarData(input_fpath)
            data = loader.load()['radar']
        elif 'rain' in input_fpath:
            loader = RawRainData(input_fpath)
            data = loader.load()['rain']
        dt = loader.datetime()
        if self.overwrite is False and os.path.exists(self.target_path(dt, fname.name)):
            return
        self.create_dir(dt)
        self.save(data, dt, fname.name)
        del loader

    def target_path(self, dt: datetime, fname: str):
        return os.path.join(
            self.ddir,
            str(dt.year),
            f'{dt.year}{dt.month:02}',
            f'{dt.year}{dt.month:02}{dt.day:02}',
            fname + '.gz'
        )

    def create_dir(self, dt: datetime):
        day_dir = os.path.join(
            self.ddir,
            str(dt.year),
            f'{dt.year}{dt.month:02}',
            f'{dt.year}{dt.month:02}{dt.day:02}',
        )
        os.makedirs(day_dir, exist_ok=True)

    def save(self, data: np.array, dt: datetime, fname: str):
        fpath = self.target_path(dt, fname)
        np.savetxt(fpath, self.preprocess_data(data), fmt='%1.3f')

    def preprocess_data(self, data):
        d0, d1 = np.where(data > 0)
        sane_values = data[d0, d1]
        compressed_data = np.vstack([d0, d1, sane_values])
        return compressed_data


if __name__ == '__main__':
    # python main_compress.py /work/dong1128/database/rain_rate_ten_min/ /work/dong1128/database/rain_rate_compressed/ --workers 4
    # python main_compress.py /work/dong1128/database/radar_cropped/ /work/dong1128/database/radar_compressed/ --workers 4
    parser = argparse.ArgumentParser(prog='python main_compress.py')
    parser.add_argument('src', type=str, help='source directory.')
    parser.add_argument('dest', type=str, help='destination directory')
    parser.add_argument('--workers', type=int, default=1)
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()

    comp = DataCompressor(args.src, args.dest, overwrite=args.overwrite)
    comp.run(workers=args.workers)
