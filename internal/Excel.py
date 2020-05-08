import xlrd
import xlsxwriter
from transliterate import translit


def rus_to_eng(str):
    return translit(str, "ru")


class Excel:
    def __init__(self):
        self._map = {}

    def updateMap(self, translate=False, **kwargs):

        for k, v in kwargs.items():
            if translate:
                k = rus_to_eng(k)
            if k in self._map.keys():
                self._map[k] = v

    @staticmethod
    def col_to_num(col_str):
        """ Convert base26 column string to number. """
        expn = 0
        col_num = 0
        for char in reversed(col_str):
            col_num += (ord(char) - ord('A') + 1) * (26 ** expn)
            expn += 1

        return col_num - 1


class ExcelReader(Excel):
    def __init__(self, excel_file, sheet=0):
        super().__init__()
        """

        :param excel_file: excel filename
        :param sheet: sheet to parse
        """
        self.__book = xlrd.open_workbook(excel_file)
        self.__worksheet = self.__book.sheet_by_index(sheet)

    def _readAllRows(self):
        return [self.__worksheet.row_values(x) for x in
                range(self.__worksheet.nrows)]

    def read_and_map(self):
        l = []
        for x in self._readAllRows():
            d = {}
            # x now a list with values
            for k, v in self._map.items():
                d[k] = x[v]
            l.append(d)
        return l


class ExcelWriter(Excel):
    def __init__(self, excel_file):
        super().__init__()

        self.__book = xlsxwriter.Workbook(excel_file)
        self.__worksheet = self.__book.add_worksheet()

        self.__lastRow = 0

    def _writeMapRow(self):
        col = 0
        for k in self._map.keys():
            self.__worksheet.write(0, col, k)
            col += 1
        self.__lastRow = 1

    def writeRow(self, row: dict):
        for k, v in row.items():
            self.__worksheet.write(self.__lastRow, self._map[k], v)
        self.__lastRow += 1

    def saveClose(self):
        self.__book.close()

    def writeAll(self, l: list):
        for x in l:
            self.writeRow(x)
