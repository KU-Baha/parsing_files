#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys as Sys
import os as Os
import pathlib as Pt
import re as Re
import numpy as Np
from xml.dom import minidom
import multiprocessing as Mp
import math as Mt

Sys.setrecursionlimit(15000)


class BaseParser:
    debug = False
    params = None
    manager = None
    managerProcess = None
    cutPartsPdf = Mt.ceil(int(Mp.cpu_count()) / 1)
    minimumColumns = 3

    pathHandlerSite = '/opt/php81/bin/php /var/www/www-root/data/www/costana.testdom.online/artisan parser_check:check '
    paramsHandlerSite = ["fileId", "objectId", "projectId", "status", "statusText"]
    directory = {"in": None, "out": None}
    file = {"in": None, "out": None}
    extentions = [".xls", ".doc", ".xlsx", ".docx", ".pdf"]
    sizesPages = {
        'a4': {'width': 595, 'height': 842},
        'a3': {'width': 842, 'height': 1191}
    }
    data = []
    dataOutput = []
    dataColumnsSearch = []
    dataColumnsSearchLength = 0
    dataColumns = {
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
    dataColumnsResult = [
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
        print(params)
        errors = []

        if params is not None:
            self.params = params

        if directory is not None:
            if directory["in"] is not None:
                self.directory["in"] = directory["in"]
            else:
                errors.append("ERR_DIR_IN")

            if directory["out"] is not None:
                self.directory["out"] = directory["out"]
            else:
                errors.append("ERR_DIR_OUT")
        else:
            errors.append("ERR_DIR")

        if file is not None:
            if file["in"] is not None:
                self.file["in"] = file["in"]
            else:
                errors.append("ERR_FILE_IN")

            if directory["out"] is not None:
                self.file["out"] = file["out"]
            else:
                errors.append("ERR_FILE_OUT")
        else:
            errors.append("ERR_FILE")

        if len(errors):
            self.errorsSignal(errors)
        else:
            self.check_directory()

    def check_directory(self):
        errors = []

        if Os.path.exists(self.directory["in"]) == False:
            errors.append("ERR_DIR_IN_EXIST" + self.directory["in"])

        if Os.path.exists(self.directory["out"]) == False:
            Os.mkdir(self.directory["out"])

        if len(errors):
            self.errorsSignal(errors)
        else:
            self.check_file()

    def check_file(self):

        errors = []

        if Os.path.exists(self.file["in"]) == False:
            errors.append("ERR_FILE_IN_EXIST " + self.file["in"])

        if Os.path.exists(self.file["out"]) == False:
            open(self.file["out"], "w").close()

        if len(errors):
            self.errorsSignal(errors)
        else:
            self.check_file_extension()


    def ps_cleaner(self, df):

        df.replace(to_replace='\(cid\:[0-9]+\)', value='', inplace=True, regex=True)
        df.replace(to_replace='[\\n\\r\\t]', value='', inplace=True, regex=True)
        df.replace(to_replace='None', inplace=True, value=Np.nan)
        df.replace(Np.nan, '', regex=True, inplace=True)
        df.dropna(axis=0, inplace=True)
        df.dropna(axis=1, inplace=True)
        df.drop_duplicates(keep="first", inplace=True)

        return df

    def prepareData(self, data):

        current_data = data

        for indexRow, row in enumerate(current_data):
            if len(row) < self.minimumColumns:
                current_data.remove(row)
                self.prepareData(data)
                break

            else:
                if not self.prepareRowAfter(row):
                    current_data.remove(row)
                    self.prepareData(data)
                    break

        return current_data;

    def prepareRowBefore(self, row):

        var = 0

        for indexCol, col in enumerate(row):
            if col is not None:
                var += 1

        return var

    def prepareRowAfter(self, row):

        var = 0

        for indexCol, col in enumerate(row):
            tmp = Re.sub(r"[^А-Яа-яёЁ]", "", str(col), 0, Re.MULTILINE)  # [^A-Za-zА-Яа-я]

            if len(tmp):
                var += 1

        return var

    def preparePageTableHead(self, index, page):

        mergeRow = False
        lastIndexRow = None
        lastRow = None

        for indexRow, row in enumerate(page):
            if mergeRow == True:
                newRow = self.mergeRow(lastRow, row)
                page.insert(lastIndexRow, newRow)
                del page[lastIndexRow + 1]
                del page[lastIndexRow + 1]
                self.preparePageTableHead(index, page)
                break

            for indexCell, cell in enumerate(row):
                cell = str(cell).strip()

                if len(cell):
                    symbol = cell[-1]

                    if symbol == ',' or symbol == '-':

                        entry = False
                        columns = self.dataColumns.copy()

                        for column in dict(columns):
                            for columnElement in columns[column]:
                                result = Re.match(r"^" + columnElement.lower(), str(cell).lower())

                                if result is not None:
                                    entry = True
                                    break

                        if entry == True:
                            mergeRow = True
                            break

            lastIndexRow = indexRow
            lastRow = row

    def preparePageTableBody(self, index, page):

        mergeRow = False
        lastIndexRow = None
        lastRow = None

        for indexRow, row in enumerate(page):
            if mergeRow == True:
                newRow = self.mergeRow(lastRow, row)
                page.insert(lastIndexRow, newRow)
                del page[lastIndexRow + 1]
                del page[lastIndexRow + 1]
                self.preparePageTableHead(index, page)
                break

            for indexCell, cell in enumerate(row):
                cell = cell.strip()

                if len(cell):
                    symbol = cell[-1]

                    if symbol == ',' or symbol == '-':
                        mergeRow = True
                        break

            lastIndexRow = indexRow
            lastRow = row

    def mergeRow(self, firstRow, lastRow):

        row = []

        if firstRow is not None and lastRow is not None:
            for index, value in enumerate(firstRow):
                if lastRow[index] is not None:
                    if len(value):
                        symbol = value[-1]

                        if symbol == ',' or symbol == '-':
                            row.append(value + lastRow[index])
                        else:
                            row.append(value + " " + lastRow[index])
                    else:
                        row.append(lastRow[index])
                else:
                    row.append(value)

        return row

    def searchHead(self, row, step=1):

        output = {}
        hiddenColumns = []
        columns = self.dataColumns.copy()

        for indexCell, valueCell in enumerate(row):
            valueCell = str(valueCell)

            if len(valueCell):
                for column in dict(columns):
                    for columnElement in columns[column]:

                        valueCell = valueCell.strip()
                        valueCell = Re.sub(r"[^\w]|[_][^,]", "", valueCell, 0, Re.MULTILINE)

                        if valueCell is not None:
                            result = Re.match(r"^" + columnElement.lower(), valueCell.lower())

                            if result is not None:
                                output[column] = indexCell

                                if column in columns:
                                    del columns[column]

        if len(output):
            return {"output": output, "length": len(row)}

    def searchHeadAfter(self, result):

        if result is not None and "output" in result and "length" in result:
            if result["output"] is not None and result["length"] is not None:
                if result["length"] >= self.minimumColumns and len(result["output"]) >= self.minimumColumns:
                    self.dataColumnsSearch = result["output"]
                    self.dataColumnsSearchLength = result["length"]

    def searchHeadReset(self):

        self.dataColumnsSearch = []
        self.dataColumnsSearchLength = 0

    def searchData(self, row):

        result = {}

        if (len(row) == self.dataColumnsSearchLength):
            for column in self.dataColumnsSearch:
                index = self.dataColumnsSearch[column]

                if row[index] is not None:
                    result[column] = row[index]

        if len(result):
            return result

    def prepareSignal(self, status, statusText=[""]):

        command = ""

        if self.pathHandlerSite is not None and len(
                self.pathHandlerSite) and self.paramsHandlerSite is not None and len(self.paramsHandlerSite):
            command = self.pathHandlerSite

            for param in self.paramsHandlerSite:

                value = ""

                if param in self.params:
                    value = self.params[param]

                if param == "status":
                    value = status

                if param == "statusText":
                    value = "".join(statusText)

                command += "=".join(["--" + param, '"' + str(value) + '"'])
                command += " "

        # print(command)

        return command

    def successSignal(self):

        print('status -> success')

        if self.debug is not None and self.debug == False:
            Os.system(self.prepareSignal(1))

        Sys.exit()

    def errorsSignal(self, errors):

        print('status -> errors', errors)

        if self.debug is not None and self.debug == False:
            Os.system(self.prepareSignal(0, errors))

        Sys.exit()

    def handlerData(self):

        if self.data:

            if len(self.data):
                self.handlerDataBefore()
                self.handlerDataAfter()

            if len(self.dataOutput):
                self.handlerDataFinish()
                self.successSignal()
            else:
                errors = ['ERR_SEARCH_PARSE_0']
                self.errorsSignal(errors)

    def handlerDataBefore(self):

        for indexPage, page in enumerate(self.data):
            self.preparePageTableHead(indexPage, page)

        # for indexPage, page in enumerate(self.data):

        #    self.preparePageTableBody(indexPage, page)

    def handlerDataAfter(self):

        for indexPage, page in enumerate(self.data):
            if len(page):
                for indexRow, row in enumerate(page):
                    if not len(self.dataColumnsSearch):
                        result = self.searchHead(row)

                        if result is not None and "output" in result and "length" in result:
                            self.searchHeadAfter(result)

                    else:

                        result = self.searchHead(row, 2)

                        if result is not None and "output" in result and "length" in result:
                            self.searchHeadAfter(result)
                        else:

                            result = self.searchData(row)

                            if result is not None:
                                self.dataOutput.append(result)
                            else:
                                self.searchHeadReset()

                    del page[indexRow]

                    if len(page) == 0:
                        del self.data[indexPage]

                    self.handlerDataAfter()

                    break

    def handlerDataFinish(self):

        xml = minidom.Document()
        root = xml.createElement('root')
        xml.appendChild(root)
        elements = xml.createElement('elements')
        root.appendChild(elements)

        for row in self.dataOutput:

            type = 'element'
            empty = 0

            for cell in row:
                value = str(row[cell])

                if not len(value):
                    empty += 1

            if empty != len(row):
                if len(row) - empty == 1 and "name" in row:
                    if len(row["name"]):
                        type = 'category'

                element = xml.createElement('element')
                element.setAttribute('type', type)

                for column in self.dataColumnsResult:
                    if type == 'category' and column != 'name':
                        break

                    elementCell = xml.createElement(column)

                    if column in row:
                        elementCell.appendChild(xml.createTextNode(str(row[column])))

                    element.appendChild(elementCell)

                elements.appendChild(element)

        with open(self.file["out"], "wb") as file:
            file.write(xml.toprettyxml(indent="\t", encoding="utf-8"))
