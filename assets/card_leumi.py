import re
from collections import OrderedDict
from common import AssetBase, format_value
from bank_leumi import BankLeumi


class CardLeumi(AssetBase):
    TOTAL_RE = '<pCreditCardNeg>(.+?)</pCreditCardNeg>'

    def __init__(self, username, password):
        super(CardLeumi, self).__init__(username, password)

    def _establish_session(self, username, password):
        self._bank_instance = BankLeumi(username, password)
        return self._bank_instance._session

    def get_next(self):
        return 0

    def get_values(self):
        summery_page = self._session.get(BankLeumi.HOME_URL).text
        val_matchobj = re.search(self.TOTAL_RE, summery_page)
        if val_matchobj is None:
            return OrderedDict([("Credit", 0)])
        val = val_matchobj.group(1).decode('base64')[5:]
        credit = format_value(val, 'credit')
        return OrderedDict([("Credit", 0-credit)])