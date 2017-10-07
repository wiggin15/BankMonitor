import re
import requests
from assets.common import StockBrokerBase, format_value


class StockFidelityNetBenefits(StockBrokerBase):
    LOGIN_URL = "https://login.fidelity.com/ftgw/Fas/Fidelity/PWI/Login/Response/dj.chf.ra/"
    SUMMARY_URL = "https://netbenefitsww.fidelity.com/mybenefitsww/stockplans/navigation/PlanSummary"

    def _establish_session(self, username, password):
        s = requests.Session()
        post_data = {"username": username, "password": password, "SavedIdInd": "N"}
        s.post(self.LOGIN_URL, data=post_data)
        return s

    def get_exercisable(self):
        summary_data_str = self._session.get(self.SUMMARY_URL).text
        match = re.search("""<sup class="dollar">.+?</sup>(.+?)<span class="currency">""", summary_data_str)
        return format_value(match.group(1), "Total")

    def get_vested(self):
        return 0

    def get_unvested(self):
        return 0
