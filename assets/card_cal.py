# coding=utf-8
import re
import requests
from common import CardBase, format_value, print_value


class CardCal(CardBase):
    CARD_LOGIN_URL = "https://services.cal-online.co.il/card-holders/Screens/AccountManagement/Login.aspx"
    CARD_HOME_URL = "https://services.cal-online.co.il/CARD-HOLDERS/SCREENS/AccountManagement/HomePage.aspx"
    CARD_DETAIL_URL = "https://services.cal-online.co.il/CARD-HOLDERS/SCREENS/AccountManagement/CardDetails.aspx"
    CARD_VALUE_RE = """<span id="%s" class="money"><b>(.*?)</b></span>"""

    def _establish_session(self, username, password):
        s = requests.Session()
        post_data = {"username": username, "password": password}
        result = s.post(self.CARD_LOGIN_URL, data=post_data).text
        assert u"ניהול ההוצאות בכרטיס האשראי" in result
        return s

    def __get_card_value(self, card_data, card_code, print_name=None):
        val = re.search(self.CARD_VALUE_RE % (card_code,), card_data).group(1)
        return format_value(val, print_name)

    def __get_balance(self, card_code):
        home_data = self._session.get(self.CARD_HOME_URL)
        card_details_queries = re.findall("(\?cardUniqueID=\d+)", home_data.text)
        card_datas = [self._session.get(self.CARD_DETAIL_URL + card_details_query)
                      for card_details_query in card_details_queries]
        assert len(card_datas) > 0
        return sum(self.__get_card_value(card_data.text, card_code) for card_data in card_datas)

    def _get_credit(self):
        card_total = self.__get_balance("lblTotalRemainingSum")
        print_value(0 - card_total, "Credit")
        return 0 - card_total

    def _get_next(self):
        return self.__get_balance("lblNextDebitSum")
