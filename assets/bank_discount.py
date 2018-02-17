import re
import requests
from collections import OrderedDict

from assets import stats
from common import BankBase, format_value


# username is in format <id>,<code>

class BankDiscount(BankBase):
    LOGIN_URL = "https://start.telebank.co.il/LoginPages/LogonMarketing2?pagekey=home&multilang=he&t=p&bank=d"
    LOGIN_COOKIE_URL = "https://start.telebank.co.il/LoginPages/vs/vsen.jsp"
    LOGIN_POST_URL = "https://start.telebank.co.il/LoginPages/Dispatcher"
    ACCOUNT_PAGE = "https://start.telebank.co.il/wps/myportal/D-H-Retail/OSH_LENTRIES_ALTAMIRA"
    VALUE_RE = '<label\s+id="lst_acc_bal"\s+name="lst_Acc_BAl"\s+>\s*([^<]+)</label>'

    def _encrypt_pwd(self, s, pwd):
        from Crypto.PublicKey import RSA
        from Crypto.Cipher import PKCS1_v1_5

        MAGIC_COOKIE_NAME = "G4CmE"  # cookie containing RSA public key for encryption
        MAGIC_COOKIE_PATTERN = "3ba782e1"  # magic string used as a splitter to find the RSA key in cookie
        RSA_EXPONENT = "10001"  # constant exponent used for RSA public key
        PASSWORD_PRE_ENC_PREFIX = "[ENC]"  # added to password before encrypting it
        PASSWORD_DELIMETER = "|@|"
        PASSWORD_SUFFIX = "|(#)|"

        cookie = s.cookies.get(MAGIC_COOKIE_NAME)
        n = long(cookie.split(MAGIC_COOKIE_PATTERN)[1][8:], 16)
        e = long(RSA_EXPONENT, 16)
        rsa = RSA.RSAImplementation()
        pub = rsa.construct((n, e))
        cipher = PKCS1_v1_5.new(pub)
        pwd = PASSWORD_PRE_ENC_PREFIX + pwd
        res = ""
        for i in range(0, len(pwd), 7):
            part = pwd[i:i + 7]
            res += cipher.encrypt(part).encode("hex") + PASSWORD_DELIMETER
        res = res[:-3] + PASSWORD_SUFFIX
        return res

    def _establish_session(self, username, password):
        s = requests.Session()
        s.get(self.LOGIN_URL)
        s.get(self.LOGIN_COOKIE_URL)
        pwd = self._encrypt_pwd(s, password)
        username_id, username_aid = username.split(",", 1)
        username = "00001" + username_id.zfill(9)
        data = dict(username=username, password=pwd, aidvalue=username_aid, aidtype="aid")
        s.post(self.LOGIN_POST_URL, data=data)
        return s

    def get_values(self, stats_dict):
        account_html = self._session.get(self.ACCOUNT_PAGE).text
        value_text = re.search(self.VALUE_RE, account_html).group(1)
        val = format_value(value_text)
        stats_dict.get_stat(stats.StatType.STAT_BANK).add(val)
        return OrderedDict([("Bank", val)])
