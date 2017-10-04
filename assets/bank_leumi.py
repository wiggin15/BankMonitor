import cookielib
import re
import urllib
import urllib2
from collections import OrderedDict
from common import BankBase, format_value


class BankLeumi(BankBase):
    LOGIN_URL = "https://hb2.bankleumi.co.il/H/Login.html"
    LOGIN_POST_URL = "https://hb2.bankleumi.co.il/InternalSite/Validate.asp"
    HOME_URL = "https://hb2.bankleumi.co.il/uniquesig0/ebanking/SO/SPA.aspx#/hpsummary"
    CHECKING_RE = r'{\\"AccountType\\":\\"CHECKING\\",\\"TotalPerAccountType\\":(.+?)}'
    HOLDINGS_RE = r'{\\"AccountType\\":\\"SECURITIES\\",\\"TotalPerAccountType\\":(.+?)}'
    DEPOSIT_RE = r'{\\"AccountType\\":\\"CD\\",\\"TotalPerAccountType\\":(.+?)}'

    def _establish_session(self, username, password):
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.open(self.LOGIN_URL)
        post_data = {'system': 'test', 'uid': username, 'password': password, 'command': 'login'}
        post_data_str = urllib.urlencode(post_data)
        opener.open(self.LOGIN_POST_URL, data=post_data_str)

        self._summery_page = opener.open(self.HOME_URL).read()

        return opener

    def _get_checking_balance(self):
        val_matchobj = re.search(self.CHECKING_RE, self._summery_page)
        val = val_matchobj.group(1)
        return format_value(val, 'checking')

    def _get_holdings_balance(self):
        val_matchobj = re.search(self.HOLDINGS_RE, self._summery_page)
        val = val_matchobj.group(1)
        return format_value(val, 'holdings')

    def _get_deposit_balance(self):
        val_matchobj = re.search(self.DEPOSIT_RE, self._summery_page)
        if val_matchobj is None:
            return 0
        val = val_matchobj.group(1)
        return format_value(val, 'deposit')

    def get_values(self):
        return OrderedDict([("Checking", self._get_checking_balance()),
                            ("Holdings", self._get_holdings_balance()),
                            ("Deposit", self._get_deposit_balance())])
