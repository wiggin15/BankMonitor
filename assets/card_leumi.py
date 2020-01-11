import requests

from .bank_leumi import BankLeumi
from .common import CardBase, print_value


class CardLeumi(CardBase):
    TOTAL_RE = r'{\\"AccountType\\":\\"CREDITCARD\\",\\"TotalPerAccountType\\":(.+?)}'

    def __init__(self, asset_section, **asset_options):
        # type: (str, ...) -> None
        super(CardLeumi, self).__init__(asset_section, **asset_options)
        self.__bank_instance = BankLeumi(asset_section, print_info=False, **asset_options)

    def _establish_session(self, username, password):
        # type: (str, str) -> requests.Session
        # noinspection PyTypeChecker
        return None

    def _get_credit(self):
        # type: () -> float
        credit = self.__bank_instance.get_total_values()['Creditcard']
        print_value(credit, 'Credit')
        return credit

    def _get_next(self):
        # type: () -> float
        return 0
