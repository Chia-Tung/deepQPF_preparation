from datetime import datetime
from pathlib import Path

class TimeUtil:

    @staticmethod
    def parse_filename_to_time(
        filename: Path, 
        format: str = "%Y%m%d_%H%M.nc"
    ):
        filename = filename.name
        return datetime.strptime(filename, format)
    
    @classmethod
    def get_filename_from_time(
        cls,
        root_path: Path,
        dt: datetime,
        format: str = "%Y%m%d_%H%M.nc"
    ) -> Path:
        year = dt.year
        month = dt.month
        day = dt.day
        return root_path/f"{year}"/f"{year}{month:02d}"/\
            f"{year}{month:02d}{day:02d}"/dt.strftime(format)
