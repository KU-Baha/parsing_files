import sys

from config import GUI
from gui import gui_mode
from utils import check_file_extension, check_args, run_handler

if __name__ == "__main__":
    if GUI:
        gui_mode()
    else:
        _, *args = sys.argv
        params = check_args(args=args)
        extention = check_file_extension(file_path=params.get("fileIn"))
        run_handler(params, extention)
