import argparse

from src.feather_compressor import FeatherCompressor
from src.data_compressor import DataCompressor

if __name__ == '__main__':
    # python main_compress.py /work/dong1128/database/rain_rate_ten_min/ /work/dong1128/database/rain_rate_ten_min_compressed/ --workers 4
    # python main_compress.py /work/dong1128/database/radar_2d_cropped/ /work/dong1128/database/radar_2d_cropped_compressed/ --workers 4
    # python main_compress.py /bk2/handsomedong/deepQPF_DB/rain_rate_ten_min/ /bk2/handsomedong/deepQPF_DB/rain_rate_ten_min_feather --workers 4
    parser = argparse.ArgumentParser(prog='python main_compress.py')
    parser.add_argument('src', type=str, help='source directory.')
    parser.add_argument('dest', type=str, help='destination directory')
    parser.add_argument('--workers', type=int, default=1)
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()

    comp = FeatherCompressor(args.src, args.dest, overwrite=args.overwrite)
    comp.run(workers=args.workers)
