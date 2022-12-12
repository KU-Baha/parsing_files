import sys
import pathlib

from config import params, extentions
from module import excel_parser, pdf_parser, word_parser


def check_file_extension(file_path: str) -> str:
    extention = pathlib.Path(file_path).suffix

    if extention not in extentions:
        print(f"Файл с расширением {extention} не допустим!")
        print(f"Список допустимых расширений: {extention}")
        return ''

    return extention


def check_args(args: list):
    if not args:
        print('Аргументы обязательны!')

        for param in params:
            print(f'- {param}')

        sys.exit()

    error_list = []
    params_error = False

    for argument in args:
        argument_data = argument.replace('--', '').split('=')

        if len(argument_data) != 2:
            error_list.append(argument)
            params_error = True

        if argument_data[0] in params:
            params[argument_data[0]] = argument_data[1]

    if params_error:
        print(f'Ошибки с аргументами: {error_list}')
        sys.exit()

    return params


def main(params: dict):
    extention = check_file_extension(file_path=params.get("directoryIn"))

    if extention == '.xls' or extention == '.xlsx':
        excel_parser.ExcelParser(params=params,
                                 directory={"in": params["directoryIn"], "out": params["directoryOut"]},
                                 file={"in": params["fileIn"], "out": params["fileOut"]})
    elif extention == '.doc' or extention == '.docx':
        word_parser.WordPaser(params=params,
                              directory={"in": params["directoryIn"], "out": params["directoryOut"]},
                              file={"in": params["fileIn"], "out": params["fileOut"]})
    elif extention == '.pdf':
        pdf_parser.PdfParser(params=params,
                             directory={"in": params["directoryIn"], "out": params["directoryOut"]},
                             file={"in": params["fileIn"], "out": params["fileOut"]})
    else:
        print("Расширение не поддерживается!")
    # Parser(params=params,
    #        directory={"in": params["directoryIn"], "out": params["directoryOut"]},
    #        file={"in": params["fileIn"], "out": params["fileOut"]})


if __name__ == "__main__":
    _, *args = sys.argv
    params = check_args(args=args)
    main(params)
