import json
import requests
from .common import CardBase, format_value


class CardIsracard(CardBase):
    LOGIN_URL = "https://digital.isracard.co.il/personalarea/Login/"
    LOGIN_VALIDATE_URL = "https://digital.isracard.co.il/services/ProxyRequestHandler.ashx?reqName=ValidateIdData"
    LOGIN_POST_URL = "https://digital.isracard.co.il/services/ProxyRequestHandler.ashx?reqName=performLogonI"
    CARD_DATA_URL = "https://digital.isracard.co.il/services/ProxyRequestHandler.ashx?reqName=DashboardCharges&format=Json&cardIdx=&returnDataStructureLevel=1&cardIndexes=&accountNumber=&actionCode=0&identityId="

    def __init__(self, asset_section, user_id=None, card_suffix=None, **asset_options):
        self.__user_id = user_id
        self.__card_suffix = card_suffix
        if not self.__user_id or not self.__card_suffix:
            raise Exception("{} user ID or card suffix are missing".format(asset_section.capitalize()))
        super(CardIsracard, self).__init__(asset_section, user="dummy", **asset_options)

    def _establish_session(self, username, password):
        headers = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8"}
        s = requests.Session()
        s.get(self.LOGIN_URL)

        data = {
            "id": self.__user_id,
            "cardSuffix": self.__card_suffix,
            "checkLevel": "1",
            "companyCode": "11",
            "idType": "1",
            "countryCode": "212",
        }
        post_data_str = json.dumps(data)
        result_str = s.post(self.LOGIN_VALIDATE_URL, data=post_data_str, headers=headers).text
        result = json.loads(result_str)
        assert result["Header"]["Status"] == "1"

        data = {
            "MisparZihuy": self.__user_id,
            "cardSuffix": self.__card_suffix,
            "idType": "1",
            "countryCode": "212",
            "Sisma": password,
        }
        post_data_str = json.dumps(data)
        s.post(self.LOGIN_POST_URL, data=post_data_str, headers=headers)
        return s

    def get_credit(self):
        card_data_raw = self._session.get(self.CARD_DATA_URL).text
        card_data = json.loads(card_data_raw)
        upcoming_billing = card_data["DashboardChargesBean"]["inOut"][0]["nextTotalsInOut"][0]["billingSumSekelInOut"]
        return format_value("-" + upcoming_billing, 'Credit')
