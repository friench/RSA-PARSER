from internal.Excel import ExcelWriter, ExcelReader


class RSAExcelWriter(ExcelWriter):
    def __init__(self, excel_file):
        super().__init__(excel_file)

        self._map = {
            "Номер договора ОСАГО": 0,
            "Серия договора ОСАГО": 1,
            "Страховая компания": 2,
            "Дата заключения договора": 3,
            "Дата начала действия договора": 4,
            "Дата окончания действия договора": 5,
            "Статус договора ОСАГО": 6,
            "Ограничение лиц допущенных к управлению ТС": 7
        }

        self._writeMapRow()


class RSAExcelReader(ExcelReader):
    def __init__(self, excel_file):
        super().__init__(excel_file, sheet=0)
        self._map = {
            "ID": 0,
            "Дата": 1,
            "Регистрационный номер авто": 2,
            "Номер кузова": 3,
            "Фирма-производитель": 4,
            "Модель авто": 5,
            "Год выпуска": 6,
            "VIN": 7
        }
        """
        self.__map defines a mask to parse rsa input file by columns
        so for example the third column is a bodyNumber
        """