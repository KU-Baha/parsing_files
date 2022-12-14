import sys
import pathlib

from config import params_dict, extentions
from module import excel_parser, pdf_parser, word_parser


def check_args(args: list) -> dict:
    if not args:
        print('Аргументы обязательны!')

        for param in params_dict:
            print(f'- {param}')

        sys.exit()

    error_list = []
    params_error = False

    for argument in args:
        argument_data = argument.replace('--', '').split('=')

        if len(argument_data) != 2:
            error_list.append(argument)
            params_error = True

        if argument_data[0] in params_dict:
            params_dict[argument_data[0]] = argument_data[1]

    if params_error:
        print(f'Ошибки с аргументами: {error_list}')
        sys.exit()

    return params_dict


def check_file_extension(file_path: str) -> str:
    extention = pathlib.Path(file_path).suffix

    if extention not in extentions:
        print(f"Файл с расширением {extention} не допустим!")
        print(f"Список допустимых расширений: {extention}")
        sys.exit()

    return extention


def run_handler(params: dict, extention: str) -> None:
    if extention == '.xls' or extention == '.xlsx':
        parser = excel_parser.ExcelParser(params=params,
                                          directory={"in": params["directoryIn"], "out": params["directoryOut"]},
                                          file={"in": params["fileIn"], "out": params["fileOut"]})
        parser.excel_handler()
    elif extention == '.doc' or extention == '.docx':
        parser = word_parser.WordPaser(params=params,
                                       directory={"in": params["directoryIn"], "out": params["directoryOut"]},
                                       file={"in": params["fileIn"], "out": params["fileOut"]})
        parser.word_handler(extention)
    elif extention == '.pdf':
        parser = pdf_parser.PdfParser(params=params,
                                      directory={"in": params["directoryIn"], "out": params["directoryOut"]},
                                      file={"in": params["fileIn"], "out": params["fileOut"]})
        parser.pdf_handler()
    else:
        print("Расширение не поддерживается!")
