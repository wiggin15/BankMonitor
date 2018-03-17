import re
from bank_leumi import BankLeumi
from common import format_value, CardBase


class CardLeumi(CardBase):
    TOTAL_RE = r'{\\"AccountType\\":\\"CREDITCARD\\",\\"TotalPerAccountType\\":(.+?)}'

    def __init__(self, asset_section, **asset_options):
        super(CardLeumi, self).__init__(asset_section, **asset_options)
        self.__bank_instance = BankLeumi(asset_section, **asset_options)

    def _establish_session(self, username, password):
        return None

    def get_credit(self):
        val_matchobj = re.search(self.TOTAL_RE, self.__bank_instance.get_summery_page())
        if val_matchobj is None:
            return format_value("0", 'Credit')
        val = val_matchobj.group(1)
        credit = format_value(val, 'Credit')
        return credit

    def get_next(self):
        return 0
