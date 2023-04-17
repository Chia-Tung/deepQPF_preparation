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