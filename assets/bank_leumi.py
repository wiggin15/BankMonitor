# coding=utf-8
import re
from collections import OrderedDict
import requests

from assets import stats
from common import BankBase, format_value, HEADERS_USER_AGENT


class BankLeumi(BankBase):
    LOGIN_URL = "https://hb2.bankleumi.co.il/H/Login.html"
    LOGIN_POST_URL = "https://hb2.bankleumi.co.il/InternalSite/Validate.asp"
    HOME_URL = "https://hb2.bankleumi.co.il/uniquesig0/ebanking/SO/SPA.aspx#/hpsummary"
    CHECKING_RE = r'{\\"AccountType\\":\\"CHECKING\\",\\"TotalPerAccountType\\":(.+?)}'
    HOLDINGS_RE = r'{\\"AccountType\\":\\"SECURITIES\\",\\"TotalPerAccountType\\":(.+?)}'
    DEPOSIT_RE = r'{\\"AccountType\\":\\"CD\\",\\"TotalPerAccountType\\":(.+?)}'

    def __init__(self, asset_section, **asset_options):
        super(BankLeumi, self).__init__(asset_section, **asset_options)
        self.__summery_page = self._session.get(self.HOME_URL, headers=HEADERS_USER_AGENT).text
        assert u"ברוך הבא, כניסתך האחרונה" in self.__summery_page

    def _establish_session(self, username, password):
        s = requests.Session()
        s.get(self.LOGIN_URL, headers=HEADERS_USER_AGENT)
        post_data = {'system': 'test', 'uid': username, 'password': password, 'command': 'login'}
        s.post(self.LOGIN_POST_URL, data=post_data, headers=HEADERS_USER_AGENT)
        return s

    def __get_checking_balance(self):
        val_matchobj = re.search(self.CHECKING_RE, self.__summery_page)
        val = val_matchobj.group(1)
        return format_value(val, 'Checking')

    def __get_holdings_balance(self):
        val_matchobj = re.search(self.HOLDINGS_RE, self.__summery_page)
        val = val_matchobj.group(1)
        return format_value(val, 'Holdings')

    def __get_deposit_balance(self):
        val_matchobj = re.search(self.DEPOSIT_RE, self.__summery_page)
        if val_matchobj is None:
            return format_value("0", 'Deposit')
        val = val_matchobj.group(1)
        return format_value(val, 'Deposit')

    def get_values(self, stats_dict):
        checking = self.__get_checking_balance()
        holdings = self.__get_holdings_balance()
        deposit = self.__get_deposit_balance()
        stats_dict.get_stat(stats.StatType.STAT_BANK).add(checking + deposit)
        stats_dict.get_stat(stats.StatType.STAT_STOCK_BROKER).add(holdings)
        return OrderedDict([("Checking", checking), ("Holdings", holdings), ("Deposit", deposit)])

    def get_summery_page(self):
        return self.__summery_page
