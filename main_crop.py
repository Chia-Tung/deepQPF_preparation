import argparse
import glob
from typing import List

from src import data_cropper


def main(
    input_path: str,
    output_path: str,
    lat_crop: List[float],
    lon_crop: List[float],
    key: str
) -> None:
    # list all files
    file_list = glob.glob(f"{input_path}/**/*.nc", recursive=True)
    file_list = sorted(file_list)

    # call cropper and crop
    cropper = data_cropper.Cropper(
        file_list,
        lat_crop,
        lon_crop,
        key=key
    )
    cropper.execute(
        output_path=output_path,
        remove_old_files=False,
        max_workers=4  # multiprocess
    )


if __name__ == '__main__':
    # python main_crop.py /work/dong1128/database/radar_2d_uncropped/ /work/dong1128/database/radar_2d_cropped/ --latitude_crop 20 27 --longitude_crop 118 123.5 -k cv
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

    main(args.input_netCDF_path, args.output_netCDF_path, args.latitude_crop, args.longitude_crop,
         args.key)
