import re
import requests
from collections import OrderedDict
from common import AssetBase, format_value

class BankLeumi(AssetBase):
    LOGIN_URL = "https://hb2.bankleumi.co.il/H/Login.html"
    LOGIN_POST_URL = "https://hb2.bankleumi.co.il/InternalSite/Validate.asp"
    HOME_URL = "https://hb2.bankleumi.co.il/uniquesig0/eBanking/Accounts/PremiumSummaryNew.aspx?p=1"
    CHECKING_RE = '<lblCurrentBalanceVal>(.+?)</lblCurrentBalanceVal>'
    HOLDINGS_URL = "https://hb2.bankleumi.co.il/uniquesig0/Trade/net/trade/portf/portfviews3.aspx"
    HOLDINGS_RE = '<td nowrap="nowrap" class="positive">&#8362 (.+?)</td>'
    DEPOSIT_RE = '<pSavingsPos>(.+?)</pSavingsPos>'

    def _establish_session(self, username, password):
        s = requests.Session()
        s.get(self.LOGIN_URL)
        post_data = {'system': 'test', 'uid': username, 'password': password, 'command': 'login'}
        s.post(self.LOGIN_POST_URL, data=post_data)
        return s

    def _get_checking_balance(self):
        summery_page = self._session.get(self.HOME_URL).text
        val_matchobj = re.search(self.CHECKING_RE, summery_page)
        val = val_matchobj.group(1).decode('base64')[4:]
        return format_value(val, 'checking')

    def _get_holdings_balance(self):
        summery_page = self._session.get(self.HOLDINGS_URL).text
        val_matchobj = re.search(self.HOLDINGS_RE, summery_page)
        val = val_matchobj.group(1)
        return format_value(val, 'holdings')

    def _get_deposit_balance(self):
        summery_page = self._session.get(self.HOME_URL).text
        val_matchobj = re.search(self.DEPOSIT_RE, summery_page)
        if val_matchobj is None:
            return 0
        val = val_matchobj.group(1).decode('base64')[4:]
        return format_value(val, 'deposit')

    def get_values(self):
        return OrderedDict([("Checking", self._get_checking_balance()),
                            ("Holdings", self._get_holdings_balance()),
                            ("Deposit", self._get_deposit_balance())])

