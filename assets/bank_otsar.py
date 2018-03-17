import re
import requests
from collections import OrderedDict
from common import BankBase, format_value


class BankOtsar(BankBase):
    LOGIN_URL = "https://online.bankotsar.co.il/LoginServices/login2.do"
    HOME_URL = "https://online.bankotsar.co.il/wps/myportal/FibiMenu/Online"
    STOCK_URL = "https://online.bankotsar.co.il/wps/myportal/FibiMenu/Online/OnCapitalMarket/OnMyportfolio/AuthSecuritiesPrtfMyPFEquities"

    def _establish_session(self, username, password):
        s = requests.Session()
        post_data = {"bankId": "OTSARPRTAL", "lang": "HE", "username": username, "password": password}
        s.post(self.LOGIN_URL, data=post_data)
        return s

    def _get_values_from_main_page(self):
        main_page_html = self._session.get(self.HOME_URL).text
        OSH = re.search("current_balance[^>]+>\s*\S+\s*([^<]+)\s*", main_page_html)
        OSH = OSH.group(1)
        return format_value(OSH, 'OSH')

    def _get_stock_value(self):
        stock_html = self._session.get(self.STOCK_URL).text
        NIA = re.findall("subtotal_val[^>]+>\s*\S+\s*([^<]+)\s*", stock_html)
        NIA = NIA[-1]
        return format_value(NIA, 'NIA')

    def get_values(self):
        bank = self._get_values_from_main_page()
        stock = self._get_stock_value()
        return OrderedDict([("Bank", bank), ("Deposit", 0), ("Stock", stock), ("Car", 0)])
