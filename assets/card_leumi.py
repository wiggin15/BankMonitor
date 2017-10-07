import re
from bank_leumi import BankLeumi
from common import format_value, CardBase


class CardLeumi(CardBase):
    TOTAL_RE = r'{\\"AccountType\\":\\"CREDITCARD\\",\\"TotalPerAccountType\\":(.+?)}'

    def _establish_session(self, username, password):
        self._bank_instance = BankLeumi(username, password)
        return self._bank_instance._session

    def get_credit(self):
        val_matchobj = re.search(self.TOTAL_RE, self._bank_instance._summery_page)
        if val_matchobj is None:
            return 0
        val = val_matchobj.group(1)
        credit = format_value(val, 'Credit')
        return credit

    def get_next(self):
        return 0
