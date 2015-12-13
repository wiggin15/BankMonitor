from __future__ import print_function
import re
import requests
from collections import OrderedDict
from common import AssetBase, format_value

class BankBeinleumi(AssetBase):
    HOME_URL = "https://new.fibi-online.co.il/wps/myportal/FibiMenu/Online"
    STOCK_URL = "https://new.fibi-online.co.il/wps/myportal/FibiMenu/Online/OnCapitalMarket/OnMyportfolio/AuthSecuritiesPrtfMyPFEquities"
    LOGIN_URL = "https://new.fibi-online.co.il/LoginServices/login2.do"
    BALANCE_PATTERN = """<span dir="ltr" class="current_balance\s+\S+\s+([^<]+)</span>"""

    def _establish_session(self, username, password):
        s = requests.Session()
        s.get("https://new.fibi-online.co.il/wps/portal")
        data = {"bankId": "FIBIPORTAL", "lang": "HE", "username": username, "password": password}
        s.post(self.LOGIN_URL, data=data)
        return s

    def _get_accounts(self):
        main_html = self._session.get(self.HOME_URL).text
        return re.findall('option value="([^"]+)"', main_html)

    def _switch_account(self, account):
        main_html = self._session.get(self.HOME_URL).text
        base_href = re.search('<base href="([^"]+)">', main_html).group(1)
        form_action = re.search('<form method="post" action="([^"]+)" name="refreshPortletForm" id="refreshPortletForm">', main_html).group(1)
        data = dict(PortletForm_ACTION_NAME="changeAccount", portal_current_account=account)
        self._session.post(base_href + form_action, data=data)

    def _get_values_from_main_page(self):
        main_html = self._session.get(self.HOME_URL).text
        OSH = re.search(self.BALANCE_PATTERN, main_html)
        OSH = OSH.group(1)
        return format_value(OSH)

    def _get_stock_value(self):
        stock_html = self._session.get(self.STOCK_URL).text
        match_obj = re.search('"fibi_amount">\s*(\S+?)\s*<', stock_html)
        if match_obj is None:
            return 0
        NIA = match_obj.group(1)
        return format_value(NIA)

    def get_values(self):
        bank = 0
        stock = 0
        for account in self._get_accounts():
            self._switch_account(account)
            bank += self._get_values_from_main_page()
            stock += self._get_stock_value()
        print("OSH: {:10,.2f}".format(bank))
        print("NIA: {:10,.2f}".format(stock))
        return OrderedDict([("Bank", bank), ("Deposit", 0), ("Stock", stock), ("Car", 0)])
