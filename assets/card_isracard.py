import re
import requests
from collections import OrderedDict
from common import CardBase, format_value


class CardIsracard(CardBase):
    ISRACARD_PAGE = "https://service.isracard.co.il/isracard/isracard"
    TRANSACTION_ID = "RikuzChiuvimAtidiim_202"

    def _establish_session(self, username, password):
        user_id, user_name = username.split(",", 1)
        data = dict(reqName="performLogonI",
                    MisparZihuy=user_id,
                    KodMishtamesh=user_name,
                    Sisma=password)
        s = requests.Session()
        s.post(self.ISRACARD_PAGE, data=data)
        return s

    def _get_card_value(self, card_index):
        data = dict(reqName="action",
                    transactionId=self.TRANSACTION_ID,
                    csrfToken=self._csrf_token,
                    transactionType="by_card",
                    CardIndex=str(card_index))
        card_sum_page = self._session.post(self.ISRACARD_PAGE, data=data).text
        value_text = re.findall('DetailsTD">\s*(\S+)\s*</td>', card_sum_page)[-1]
        return format_value(value_text)

    def get_next(self):
        return 0

    def get_values(self):
        sum_page = self._session.get("{}?reqName={}".format(self.ISRACARD_PAGE, self.TRANSACTION_ID)).text
        num_cards_text = re.search('<option.*?value="(\d+)"\s*>[^<]+</option>\s*</select>', sum_page).group(1)
        num_cards = int(num_cards_text) + 1
        self._csrf_token = re.search('csrfToken" value="([^"]+)"', sum_page).group(1)
        card_total = sum(self._get_card_value(card_index) for card_index in range(num_cards))
        return OrderedDict([("Credit", 0 - card_total)])
