from .bank_leumi import BankLeumi
from .common import CardBase, print_value


class CardLeumi(CardBase):
    TOTAL_RE = r'{\\"AccountType\\":\\"CREDITCARD\\",\\"TotalPerAccountType\\":(.+?)}'

    def __init__(self, asset_section, **asset_options):
        super(CardLeumi, self).__init__(asset_section, **asset_options)
        self.__bank_instance = BankLeumi(asset_section, print_info=False, **asset_options)

    def _establish_session(self, username, password):
        return None

    def get_credit(self):
        credit = self.__bank_instance.get_total_values()['Creditcard']
        print_value(credit, 'Credit')
        return credit

    def get_next(self):
        return 0
