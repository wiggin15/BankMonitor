import json
import requests
from assets.common import StockBrokerBase, convert_usd_to_ils, print_value


class MorganStanleyStockPlanConnect(StockBrokerBase):
    LOGIN_URL = "https://stockplanconnect.morganstanley.com/app-bin/cesreg/Login"
    SUMMARY_URL = "https://stockplanconnect.morganstanley.com/app-bin/spc/ba/sps/summary?format=json"

    def __init__(self, asset_section, tax_percentage=0.25, **asset_options):
        super(MorganStanleyStockPlanConnect, self).__init__(asset_section, **asset_options)
        self.__tax_percentage = float(tax_percentage)
        summary_data_str = self._session.get(self.SUMMARY_URL).text
        summary_data_str = summary_data_str[summary_data_str.index("{"):]
        self.__summary_data = json.loads(summary_data_str)

    def _establish_session(self, username, password):
        s = requests.Session()
        post_data = {"username": username, "unmaskedUsername": username, "password": password}
        s.post(self.LOGIN_URL, data=post_data)
        return s

    def get_summary_value(self, value_name, print_name):
        value_str_raw = self.__summary_data[value_name]
        value = float(value_str_raw[1:].replace(",", ""))
        print_value(value, "{} original (USD)".format(print_name))
        value_ils = convert_usd_to_ils(value) * (1 - self.__tax_percentage)
        print_value(value_ils, "{} final".format(print_name))
        return value_ils

    def get_exercisable(self):
        return self.get_summary_value("totalMktvalue", "Exercisable")

    def get_vested(self):
        return 0

    def get_unvested(self):
        return self.get_summary_value("totalUnvestedvalue", "Unvested")
