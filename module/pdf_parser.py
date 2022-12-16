import math
import json
import camelot
import multiprocessing as mp
import PyPDF2 as py_pdf

from module.base import BaseParser


class PdfParser(BaseParser):
    cut_parts_pdf = math.ceil(int(mp.cpu_count()) / 1)
    manager = None
    manager_process = None

    def cut_pdf_pages(self, _list, num):
        part_len = math.ceil(len(_list) / num)
        return [_list[part_len * k:part_len * (k + 1)] for k in range(0, num)]

    def pdf_handler_filter_page_size(self, width, height, rotate, numPage):
        success = False
        width = round(float(width))
        height = round(float(height))

        if height < width:
            width, height = height, width

        for index in self.sizes_pages:
            size_page = self.sizes_pages[index]

            if 'width' not in size_page and 'height' not in size_page:
                continue

            if width <= size_page['width'] and height <= size_page['height']:
                success = True
                break

        return success

    def pdf_handler(self):
        file_in = py_pdf.PdfFileReader(self.file["in"], strict=False)

        if not file_in and file_in.getNumPages() < 0:
            self.errors_signal('ERR_FILE_ERROR')
            return

        pdf_pages = []
        pdf = py_pdf.PdfFileReader(self.file["in"], strict=False)
        num_pages = pdf.getNumPages()

        for numPage in range(0, num_pages):
            pdfPage = pdf.getPage(numPage)

            if not self.pdf_handler_filter_page_size(pdfPage.mediaBox.getWidth(), pdfPage.mediaBox.getHeight(),
                                                     pdfPage.get('/Rotate'), numPage):
                continue

            pdf_pages.append(numPage)

        num_pages = len(pdf_pages)

        if not num_pages:
            self.errors_signal('ERR_FILE_ERROR')
            return

        print('pdf_handler -> ', num_pages)
        pdf_pages = self.cut_pdf_pages(pdf_pages, self.cut_parts_pdf)

        if not len(pdf_pages):
            return

        with mp.Manager() as manager:
            self.manager = manager.list()
            self.managerProcess = list()

            for processPage in pdf_pages:
                if not len(processPage):
                    continue
                self.pdf_thread_pages_handler_start(processPage, num_pages)

            if not len(self.managerProcess):
                return

            for process in self.managerProcess:
                process.join()

    def pdf_thread_pages_handler_start(self, threadPage, num_pages):
        print(self.pdf_thread_pages_handler(threadPage, num_pages))
        # th = Mp.Process(target=self.pdf_thread_pages_handler, args=(threadPage, num_pages))
        # th.start()
        # self.managerProcess.append(th)

    def pdf_thread_pages_handler(self, pages, num_pages):
        for page in pages:
            print('pdf_thread_pages_handler -> ', page)
            self.pdf_page_handler(self.file["in"], page)
            self.pdf_thread_pages_handler_finish(num_pages)

    def pdf_thread_pages_handler_finish(self, num_pages):
        if len(self.manager) != num_pages:
            return

        result = []

        for item in self.manager:
            if item:
                result.append(item)

        self.data = result
        self.handler_data()

    def pdf_page_handler(self, path, page):
        tables = camelot.read_pdf(path, flavor='stream', edge_tol=500, row_tol=15, pages=str(page))

        if not tables:
            return

        result = None

        for table in tables:
            data = table.df
            data = self.ps_cleaner(data)
            data = json.loads(data.to_json(orient="values"))

            if not data:
                continue

            data = self.prepare_data(data)

            if not data:
                continue

            if result:
                result += data
            else:
                result = data

            # camelot.plot(table, kind='textedge').show()

        self.manager.insert(page, result)
