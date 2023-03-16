import os
import argparse

from src.cleaver import Cleaver

"""
Split 1-h accumulated rainfall (mm) into 10-m rain rate (mm/h)
"""
def main(
    inp_dir: str, 
    oup_dir: str, 
    cwd_dir: str, 
    slice_type: str,
    mask_fname: str, 
    fixed_array_fname: str
) -> None:
    # instantiate Cleaver object, all of the executions will be done via this object
    rain_cleaver = Cleaver(
        inp_dir, oup_dir, cwd_dir, slice_type, 'qperr', mask_fname, fixed_array_fname
    )
    
    rain_cleaver.run()

if __name__ == "__main__":
    # python main_rain.py /work/dong1128/database/rain_accu_ten_min/ /work/dong1128/database/rain_rate_ten_min/ -c $PWD --type last
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path", type=str, help="enter input data path")
    parser.add_argument("output_path", type=str, help="enter output data path")
    parser.add_argument("-c", "--current_path", type=str, default=os.getcwd(),
        help="current working directory stores the mask.json and fixed_size_array.json")
    parser.add_argument("--overwrite", action="store_true", default=False, 
        help="if overwrite the old output")
    parser.add_argument("--type", choices=["last", "all"], default="last", 
        help="want to slice the last frame or all of the data")
    args = parser.parse_args()

    inp_dir = args.input_path
    oup_dir = args.output_path
    cwd_dir = args.current_path
    slice_type = args.type
    mask_fname = 'mask.json'
    fixed_array_fname = 'fixedSizeArray.json'

    main(inp_dir, oup_dir, cwd_dir, slice_type, mask_fname, fixed_array_fname)