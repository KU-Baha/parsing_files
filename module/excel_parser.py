import re
import json
import pandas
import zipfile

from module.base import BaseParser


class ExcelParser(BaseParser):
    def excel_handler(self):
        sheets_names = self.excel_get_sheets(self.file["in"])

        if not len(sheets_names):
            self.handler_data()
            return

        for sheet_name in sheets_names:
            data = self.excel_load_sheet(sheet_name)
            data = self.ps_cleaner(data)
            data = json.loads(data.to_json(orient="values"))

            if not data:
                continue

            data = self.prepare_data(data)

            if not data:
                continue

            self.data.append(data)

        self.handler_data()

    def excel_load_sheet(self, name):
        sheet = pandas.read_excel(self.file["in"], engine="openpyxl", sheet_name=str(name))
        return sheet

    def excel_get_sheets(self, path):

        sheets = []

        with zipfile.ZipFile(path, 'r') as zip_ref:
            xml = zip_ref.read("xl/workbook.xml").decode("utf-8")

            for s_tag in re.findall("<sheet [^>]*", xml):
                sheets.append(re.search('name="[^"]*', s_tag).group(0)[6:])

        return sheets
