#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import os
import re
import numpy
from xml.dom import minidom
import multiprocessing as mp
import math

sys.setrecursionlimit(15000)


class BaseParser:
    debug = False
    params = None
    minimum_columns = 3

    path_handler_site = '/opt/php81/bin/php /var/www/www-root/data/www/costana.testdom.online/artisan parser_check:check '
    params_handler_site = ["fileId", "objectId", "projectId", "status", "statusText"]
    directory = {"in": None, "out": None}
    file = {"in": None, "out": None}
    extentions = [".xls", ".doc", ".xlsx", ".docx", ".pdf"]
    sizes_pages = {
        'a4': {'width': 595, 'height': 842},
        'a3': {'width': 842, 'height': 1191}
    }
    data = []
    data_output = []
    data_columns_search = []
    data_columns_search_length = 0
    data_columns = {
        'position': ['поз', 'позиция', '#', '№'],
        'name': ['наим', 'наименование', 'наз', 'название'],
        'code': ['код', 'артикул', 'арт'],
        'type': ['тип', 'марка'],
        'customer': ['завод', 'изготовитель', 'поставщик', 'фирма'],
        'unit': ['ед', 'единица', 'имерения'],
        'count': ['кол', 'кол-во', 'количество'],
        'weight': ['масса', 'вес'],
        'note': ['примечание']
    }
    data_columns_result = [
        'name',
        'code',
        'type',
        'customer',
        'unit',
        'count',
        'price_work',
        'full_price_work',
        'price_material',
        'full_price_material',
        'note'
    ]

    def __init__(self, directory, file, params):
        if params:
            self.params = params

        errors = self.validate(directory, file)

        if len(errors):
            self.errors_signal(errors)
        else:
            self.check_directory()

    def validate(self, directory, file):
        errors = []

        if directory:
            if directory.get("in"):
                self.directory["in"] = directory["in"]
            else:
                errors.append("ERR_DIR_IN")

            if directory.get("out"):
                self.directory["out"] = directory["out"]
            else:
                errors.append("ERR_DIR_OUT")
        else:
            errors.append("ERR_DIR")

        if file:
            if file.get("in"):
                self.file["in"] = file["in"]
            else:
                errors.append("ERR_FILE_IN")

            if directory.get("out"):
                self.file["out"] = file["out"]
            else:
                errors.append("ERR_FILE_OUT")
        else:
            errors.append("ERR_FILE")

        return errors

    def check_directory(self):
        errors = []

        if not os.path.exists(self.directory.get("in", "")):
            errors.append(f"ERR_DIR_IN_EXIST {self.directory.get('in')}")

        if not os.path.exists(self.directory.get("out", "")):
            os.mkdir(self.directory.get("out", ""))

        if len(errors):
            self.errors_signal(errors)
        else:
            self.check_file()

    def check_file(self):
        errors = []

        if not os.path.exists(self.file.get("in", "")):
            errors.append("ERR_FILE_IN_EXIST " + self.file.get("in", ""))

        if not os.path.exists(self.file.get("out", "")):
            open(self.file.get("out", ""), "w").close()

        if len(errors):
            self.errors_signal(errors)

    def ps_cleaner(self, df):
        df.replace(to_replace='\(cid\:[0-9]+\)', value='', inplace=True, regex=True)
        df.replace(to_replace='[\\n\\r\\t]', value='', inplace=True, regex=True)
        df.replace(to_replace='None', inplace=True, value=numpy.nan)
        df.replace(numpy.nan, '', regex=True, inplace=True)
        df.dropna(axis=0, inplace=True)
        df.dropna(axis=1, inplace=True)
        df.drop_duplicates(keep="first", inplace=True)

        return df

    def prepare_data(self, data):

        current_data = data

        for _, row in enumerate(current_data):
            if len(row) < self.minimum_columns:
                current_data.remove(row)
                self.prepare_data(data)
                break

            if not self.prepare_row_after(row):
                current_data.remove(row)
                self.prepare_data(data)
                break

        return current_data

    def prepare_row_before(self, row):
        var = 0

        for _, col in enumerate(row):
            if col:
                var += 1

        return var

    def prepare_row_after(self, row):
        var = 0

        for _, col in enumerate(row):
            tmp = re.sub(r"[^А-Яа-яёЁ]", "", str(col), 0, re.MULTILINE)  # [^A-Za-zА-Яа-я]

            if len(tmp):
                var += 1

        return var

    def prepare_page_table_head(self, index, page):
        merge_row = False
        last_index_row = None
        last_row = None

        for index_row, row in enumerate(page):
            if merge_row:
                new_row = self.merge_row(last_row, row)
                page.insert(last_index_row, new_row)
                del page[last_index_row + 1]
                del page[last_index_row + 1]
                self.prepare_page_table_head(index, page)
                break

            for index_cell, cell in enumerate(row):
                cell = str(cell).strip()

                if not len(cell):
                    continue

                symbol = cell[-1]

                if symbol != ',' or symbol != '-':
                    continue

                entry = False
                columns = self.data_columns.copy()

                for column in dict(columns):
                    for column_element in columns[column]:
                        result = re.match(r"^" + column_element.lower(), str(cell).lower())

                        if result:
                            entry = True
                            break

                if entry:
                    merge_row = True
                    break

            last_index_row = index_row
            last_row = row

    def prepare_age_table_body(self, index, page):
        merge_row = False
        last_index_row = None
        last_row = None

        for index_row, row in enumerate(page):
            if merge_row:
                new_row = self.merge_row(last_row, row)
                page.insert(last_index_row, new_row)
                del page[last_index_row + 1]
                del page[last_index_row + 1]
                self.prepare_page_table_head(index, page)
                break

            for index_cell, cell in enumerate(row):
                cell = cell.strip()

                if not len(cell):
                    continue

                symbol = cell[-1]

                if symbol != ',' or symbol != '-':
                    continue

                merge_row = True
                break

            last_index_row = index_row
            last_row = row

    def merge_row(self, first_row, last_row):
        row = []

        if not first_row and not last_row:
            return row

        for index, value in enumerate(first_row):
            if not last_row[index]:
                row.append(value)
                continue

            if not len(value):
                row.append(last_row[index])
                continue

            symbol = value[-1]

            if symbol == ',' or symbol == '-':
                row.append(value + last_row[index])
            else:
                row.append(value + " " + last_row[index])

        return row

    def search_head(self, row):

        output = {}
        columns = self.data_columns.copy()

        for index_cell, value_cell in enumerate(row):
            value_cell = str(value_cell)

            if not len(value_cell):
                continue

            for column in dict(columns):
                for column_element in columns[column]:

                    value_cell = value_cell.strip()
                    value_cell = re.sub(r"[^\w]|[_][^,]", "", value_cell, 0, re.MULTILINE)

                    if not value_cell:
                        continue

                    result = re.match(r"^" + column_element.lower(), value_cell.lower())

                    if not result:
                        continue

                    output[column] = index_cell

                    if column not in columns:
                        continue

                    del columns[column]

        if len(output):
            return {"output": output, "length": len(row)}

    def search_head_after(self, result):
        if not result and "output" not in result and "length" not in result:
            return

        if not result.get("output") and not result.get("length"):
            return

        if result.get("length") >= self.minimum_columns and len(result.get("output")) >= self.minimum_columns:
            self.data_columns_search = result.get("output")
            self.data_columns_search_length = result.get("length")

    def search_head_reset(self):
        self.data_columns_search = []
        self.data_columns_search_length = 0

    def search_data(self, row):
        result = {}

        if len(row) != self.data_columns_search_length:
            return

        for column in self.data_columns_search:
            index = self.data_columns_search[column]

            if not row[index]:
                continue

            result[column] = row[index]

        if len(result):
            return result

    def prepare_signal(self, status, status_text=[""]):
        command = ""

        if not self.path_handler_site and not len(self.path_handler_site) \
                and not self.params_handler_site and not len(self.params_handler_site):
            return command

        command = self.path_handler_site

        for param in self.params_handler_site:
            value = ""

            if param in self.params:
                value = self.params[param]

            if param == "status":
                value = status

            if param == "statusText":
                value = "".join(status_text)

            command += "=".join(["--" + param, '"' + str(value) + '"'])
            command += " "

        return command

    def success_signal(self):
        print('status -> success')

        if self.debug:
            sys.exit()

        os.system(self.prepare_signal(1))

    def errors_signal(self, errors):

        print('status -> errors', errors)

        if self.debug:
            sys.exit()

        os.system(self.prepare_signal(0, errors))

    def handler_data(self):
        if not self.data:
            return

        if len(self.data):
            self.handler_data_before()
            self.handler_data_after()

        if len(self.data_output):
            self.handler_data_finish()
            self.success_signal()
        else:
            errors = ['ERR_SEARCH_PARSE_0']
            self.errors_signal(errors)

    def handler_data_before(self):
        for index_page, page in enumerate(self.data):
            self.prepare_page_table_head(index_page, page)

    def handler_data_after(self):
        for index_page, page in enumerate(self.data):
            if not len(page):
                continue
            for index_row, row in enumerate(page):
                if not len(self.data_columns_search):
                    result = self.search_head(row)

                    if result and "output" in result and "length" in result:
                        self.search_head_after(result)
                else:
                    result = self.search_head(row, 2)

                    if result and "output" in result and "length" in result:
                        self.search_head_after(result)
                    else:
                        result = self.search_data(row)

                        if result:
                            self.data_output.append(result)
                        else:
                            self.search_head_reset()

                del page[index_row]

                if not len(page):
                    del self.data[index_page]

                self.handler_data_after()
                break

    def handler_data_finish(self):
        xml = minidom.Document()
        root = xml.createElement('root')
        xml.appendChild(root)
        elements = xml.createElement('elements')
        root.appendChild(elements)

        for row in self.data_output:
            type = 'element'
            empty = 0

            for cell in row:
                value = str(row[cell])

                if not len(value):
                    empty += 1

            if empty == len(row):
                continue

            if len(row) - empty == 1 and "name" in row:
                if len(row["name"]):
                    type = 'category'

            element = xml.createElement('element')
            element.setAttribute('type', type)

            for column in self.data_columns_result:
                if type == 'category' and column != 'name':
                    break

                elementCell = xml.createElement(column)

                if column in row:
                    elementCell.appendChild(xml.createTextNode(str(row[column])))

                element.appendChild(elementCell)

            elements.appendChild(element)

        with open(self.file.get("out", ""), "wb") as file:
            file.write(xml.toprettyxml(indent="\t", encoding="utf-8"))
