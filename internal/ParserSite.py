import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ParserSite:

    def __makeSession(self):
        self._session = requests.Session()
        return self._session

    def _getSession(self):
        return self._session if hasattr(self, "session") else self.__makeSession()

    def _requestSite(self, url, method="GET", params=None, data=None, headers=None):
        return self._getSession().request(method, url, params, data, headers, verify=False)