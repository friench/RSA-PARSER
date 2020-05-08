
import json



from internal.errors import ResponseException, CaptchaException
from internal.ParserSite import ParserSite
from internal.RSAExcel import RSAExcelWriter, RSAExcelReader
from internal.Excel import Excel
from internal.thread import WorkerThreadPool
from internal.AnticaptchaSolver import AntiCaptchaSolver
from internal import getLogger


class RSA(ParserSite):
    """
    Class for parsing https://dkbm-web.autoins.ru/dkbm-web-1.0/?
    DEV: @ractyfree

    """

    def __init__(self, excel_file: str, vin_position: str, plus_time: int, minus_time: int, mode: int,
                 anti: AntiCaptchaSolver):
        """
        :param excel_file: path to the target excel_file
        :param vin_position: column by it's number
        :param plus_time: days to add
        :param minus_time: days to reduce
        """
        self.__main_gate = "https://dkbm-web.autoins.ru/dkbm-web-1.0/"
        self.__gates = ["policy.htm", "bsostate.htm"]
        self.__site_key = "6Lf2uycUAAAAALo3u8D10FqNuSpUvUXlfP7BzHOk"

        self.__excel_file = excel_file
        self.__vin_position = vin_position
        self.__plus_time = plus_time
        self.__minus_time = minus_time
        self.__anti = anti
        self.__mode = mode
        self.__date_position = "B"

    def __formRequest(self, **kwargs):
        """
        :param **kwargs - list of parameters

        :returns dict of params
        """
        d = {}
        for k, v in kwargs.items():
            d[k] = v

        d['captcha'] = self.__anti.solveTask(self.__main_gate, self.__site_key)
        return d

    class ResponseWrappers:

        @staticmethod
        def responseValidator(func, MAX_TRIES_REQUEST=5):
            def wrapper(*args, **kwargs):
                for x in range(MAX_TRIES_REQUEST):
                    try:
                        resp = func(*args, **kwargs)
                    except json.decoder.JSONDecodeError as e:
                        getLogger().error("{}".format(e))
                        continue

                    if not resp.get("validCaptcha"):
                        if x > MAX_TRIES_REQUEST:
                            raise ResponseException("Ошибка капчи! {}".format(resp))
                        getLogger().error("Invalid captcha encountered. Trying again... Current try: {}".format(x))
                        continue

                    elif resp.get("errorMessage"):
                        if x > MAX_TRIES_REQUEST:
                            raise CaptchaException("Ошибка сервера! {}".format(resp))
                        getLogger().error("Error message encountered. Trying again... Current try: {}".format(x))
                        continue
                    else:
                        break

                return resp

            return wrapper

        @staticmethod
        def formatResponse(func):
            def wrapper(*args, **kwargs):
                l = func(*args, **kwargs)

                if kwargs.get("gate") == "policy.htm" and l.get("policyResponseUIItems"):
                    newl = []
                    for x in l['policyResponseUIItems']:
                        newl.append({
                            'Серия договора ОСАГО': x.get("policyBsoSerial"),
                            "Номер договора ОСАГО": x.get("policyBsoNumber"),
                            "Страховая компания": x.get("insCompanyName")
                        })
                    l = newl

                if kwargs.get("gate") == "bsostate.htm":
                    newl = [{
                        "Дата заключения договора": l.get('policyCreateDate'),
                        "Дата начала действия договора": l.get('policyBeginDate'),
                        "Дата окончания действия договора": l.get("policyEndDate"),
                        "Статус договора ОСАГО": l.get("bsoStatusName")
                    }]
                    l = newl
                return l

            return wrapper

    @ResponseWrappers.formatResponse
    @ResponseWrappers.responseValidator
    def __getInfo(self, gate="policy.htm", **kwargs):
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Length": "564",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "dkbm-web.autoins.ru",
            "Origin": "https://dkbm-web.autoins.ru",
            "Pragma": "no-cache",
            "Referer": "{}{}?".format(self.__main_gate, gate),
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }
        return json.loads(
            self._requestSite("{}{}".format(self.__main_gate, gate), headers=headers, method="POST",
                              data=self.__formRequest(**kwargs)).text)

    def __parseExcel(self):
        excel = RSAExcelReader(self.__excel_file)
        if self.__vin_position:
            excel.updateMap(VIN=Excel.col_to_num(self.__vin_position))

        if self.__date_position:
            excel.updateMap(translate=True, Data=Excel.col_to_num(self.__date_position))

        return excel.read_and_map()

    def __ThreadedGetInfo(self, row: dict, only_vin=False):
        ret = self.__getInfo(gate="policy.htm", vin=row.get("VIN"), date=row.get("Дата"),
                             lp=row.get("Регистрационный номер авто") if not only_vin else "",
                             bodyNumber=row.get("Номер кузова") if not only_vin else "",
                             chassisNumber="")  # idk there, mb someone knows which column is it :DDDDDD
        for x in ret:
            for y in self.__getInfo(gate="bsostate.htm", bsoseries=x['Серия договора ОСАГО'],
                                    bsonumber=x['Номер договора ОСАГО']):
                for k, v in y.items():
                    ret[ret.index(x)][k] = v
        return ret

    def __startThreaded(self, threads=60, only_vin=False):
        tpool = WorkerThreadPool(threads, False)
        return tpool.anyThread(self.__ThreadedGetInfo, self.__parseExcel(), only_vin)

    def start(self, only_vin=False):

        ret = self.__startThreaded(60, only_vin)

        writer = RSAExcelWriter("output.xls")
        writer.writeAll(ret)
        writer.saveClose()
