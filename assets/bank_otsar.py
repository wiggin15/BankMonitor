import re
import requests
from collections import OrderedDict
from common import AssetBase, format_value

class BankOtsar(AssetBase):
    LOGIN_URL = "https://www.fibi-online.co.il/web/otsar"
    HOME_URL = "https://www.fibi-online.co.il/web/TotalPosition.do?SUGBAKA=811&I-OSH-FLAG=1&I-PACHAK-FLAG=1&I-HODAOT-FLAG=1"
    KRANOT_URL = "https://www.fibi-online.co.il/web/Processing?SUGBAKA=021"
    VALUE_RE = """<td nowrap="yes">[0-9/]+</td><td nowrap="yes">(-?[0-9.,]+)</td><td nowrap="yes" dir="(?:rtl)?"><a href="\\./Processing\\?SUGBAKA=%s">"""

    def _establish_session(self, username, password):
        s = requests.Session()
        post_data = {'requestId': 'logon', 'ZIHMIST': username, 'KOD': password}
        s.post(self.LOGIN_URL, data=post_data)
        return s

    def _get_bank_value(self, bank_data, bank_code, print_name=None):
        val_matchobj = re.search(self.VALUE_RE % (bank_code,), bank_data)
        if val_matchobj is None:
            return 0
        val = val_matchobj.group(1)
        return format_value(val, print_name)

    def _get_values_from_main_page(self):
        main_page_html = self._session.get(self.HOME_URL).text
        bank = self._get_bank_value(main_page_html, "077", "OSH")
        deposit = self._get_bank_value(main_page_html, "101", "PIK")
        car = self._get_bank_value(main_page_html, "200", "CAR")
        return bank, deposit, car

    def _get_stock_value(self):
        stock_html = self._session.get(self.KRANOT_URL).text
        NIA = re.search("<td class=\"TITLE\" nowrap>\s*([0-9,.]+)\s*</td>", stock_html)
        NIA = NIA.group(1)
        return format_value(NIA, 'NIA')

    def get_values(self):
        bank, deposit, car = self._get_values_from_main_page()
        stock = self._get_stock_value()
        return OrderedDict([("Bank", bank), ("Deposit", deposit), ("Stock", stock), ("Car", car)])

