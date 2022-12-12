import math
import json
import camelot
import multiprocessing as mp
import PyPDF2 as py_pdf

from module.base import BaseParser


class PdfParser(BaseParser):
    def cut_pdf_pages(self, list, num):

        part_len = math.ceil(len(list) / num)

        return [list[part_len * k:part_len * (k + 1)] for k in range(0, num)]

    def pdf_handler_filter_page_size(self, width, height, rotate, numPage):

        success = False
        width = round(float(width))
        height = round(float(height))

        if height < width:
            width, height = height, width

        for index in self.sizesPages:

            sizePage = self.sizesPages[index]

            if 'width' in sizePage and 'height' in sizePage:

                if width <= sizePage['width'] and height <= sizePage['height']:
                    success = True
                    break

        return success

    def pdf_handler(self):

        fileIn = py_pdf.PdfFileReader(self.file["in"], strict=False)

        if fileIn is not None and fileIn.getNumPages() > 0:

            pdfPages = []
            pdf = py_pdf.PdfFileReader(self.file["in"], strict=False)
            numPages = pdf.getNumPages()

            for numPage in range(0, numPages):

                pdfPage = pdf.getPage(numPage)

                if self.pdf_handler_filter_page_size(pdfPage.mediaBox.getWidth(), pdfPage.mediaBox.getHeight(),
                                                     pdfPage.get('/Rotate'), numPage):
                    pdfPages.append(numPage)

            numPages = len(pdfPages)

            if numPages:

                print('pdf_handler -> ', numPages)

                pdfPages = self.cut_pdf_pages(pdfPages, self.cutPartsPdf)

                if len(pdfPages):
                    with mp.Manager() as manager:

                        self.manager = manager.list()
                        self.managerProcess = list()

                        for processPage in pdfPages:
                            if len(processPage):
                                self.pdf_thread_pages_handler_start(processPage, numPages)

                        if len(self.managerProcess):
                            for process in self.managerProcess:
                                process.join()
            else:
                self.errorsSignal('ERR_FILE_ERROR')

        else:
            self.errorsSignal('ERR_FILE_ERROR')

    def pdf_thread_pages_handler_start(self, threadPage, numPages):
        print(self.pdf_thread_pages_handler(threadPage, numPages))
        # th = Mp.Process(target=self.pdf_thread_pages_handler, args=(threadPage, numPages))
        # th.start()
        # self.managerProcess.append(th)

    def pdf_thread_pages_handler(self, pages, numPages):
        for page in pages:
            print('pdf_thread_pages_handler -> ', page)
            self.pdf_page_handler(self.file["in"], page)
            self.pdf_thread_pages_handler_finish(numPages)

    def pdf_thread_pages_handler_finish(self, numPages):

        if len(self.manager) == numPages:

            result = list()

            for item in self.manager:
                if item is not None:
                    result.append(item)

            self.data = result

            self.handlerData()

    def pdf_page_handler(self, path, page):
        tables = camelot.read_pdf(path, flavor='stream', edge_tol=500, row_tol=15, pages=str(page))

        if tables:
            result = None

            for table in tables:

                data = table.df
                data = self.ps_cleaner(data)
                data = json.loads(data.to_json(orient="values"))

                if data:

                    data = self.prepareData(data)

                    if data:
                        if result is not None:
                            result += data
                        else:
                            result = data

                        # camelot.plot(table, kind='textedge').show()

            self.manager.insert(page, result)
