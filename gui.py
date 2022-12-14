from tkinter import Tk, Text, Button, filedialog, messagebox

from config import extentions, params_dict
from utils import check_file_extension, run_handler

ACTIVE = "active"
NORMAL = "normal"
DISABLED = "disabled"

file_types = [f"*{ft}" for ft in extentions]
params_list = ['directoryIn', 'directoryOut', 'fileIn', 'fileOut']


def get_dir_path(name):
    dir_path = filedialog.askdirectory()
    params_dict[name] = dir_path


def get_file_path(name):
    file_path = filedialog.askopenfilename(filetypes=(('Допустимые документы', file_types), ("Все файлы", "*.*")))
    params_dict[name] = file_path


def run_parser():
    for param in params_list:
        if not params_dict[param]:
            messagebox.showerror(title="Field error!", message=f"'{param}' field can't be empty")

    extention = check_file_extension(file_path=params_dict.get("fileIn"))
    run_handler(params_dict, extention)
    messagebox.showinfo(title="Success", message=f"Success saved {params_dict['fileOut']}")


def gui_mode():
    window = Tk()
    window.title("File parsing")
    window.geometry('600x300')

    dir_in = Button(text="Directory In", command=lambda: get_dir_path(params_list[0]), state=ACTIVE)
    dir_in.pack()
    dir_out = Button(text="Directory Out", command=lambda: get_dir_path(params_list[1]), state=ACTIVE)
    dir_out.pack()

    file_in = Button(text="File In", command=lambda: get_file_path(params_list[2]), state=ACTIVE)
    file_in.pack()
    file_out = Button(text="File Out", command=lambda: get_file_path(params_list[3]), state=ACTIVE)
    file_out.pack()

    parser = Button(text="Run Parser", command=run_parser, state=NORMAL)
    parser.pack()

    window.mainloop()


if __name__ == '__main__':
    gui_mode()
