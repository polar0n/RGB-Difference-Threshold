import csv
from os.path import exists


class Data2CSV:
    def __init__(self, filename, headings):
        self.filename = filename
        self._excel_dialect = csv.excel()
        self._excel_dialect.lineterminator = '\n'
        if not exists(filename):
            self.append_row(headings)


    def append_row(self, iterable):
        with open(self.filename, 'a') as f:
            writer = csv.writer(f, dialect=self._excel_dialect)
            writer.writerow(iterable)