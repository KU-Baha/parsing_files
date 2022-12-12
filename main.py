import sys

from config import params
from parser import Parser

if __name__ == "__main__":
    _, *arguments = sys.argv

    if not arguments:
        print('Аргументы обязательны!')

        for param in params:
            print(f'- {param}')

        sys.exit()

    error_list = []
    params_error = False

    for argument in arguments:
        argument_data = argument.replace('--', '').split('=')

        if len(argument_data) != 2:
            error_list.append(argument)
            params_error = True

        if argument_data[0] in params:
            params[argument_data[0]] = argument_data[1]

    if params_error:
        print(f'Ошибки с аргументами: {error_list}')
        sys.exit()

    Parser(params=params,
           directory={"in": params["directoryIn"], "out": params["directoryOut"]},
           file={"in": params["fileIn"], "out": params["fileOut"]})
