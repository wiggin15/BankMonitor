import json
import requests
from .common import WorkStockBase, convert_usd_to_ils, print_value


class MorganStanleyStockPlanConnect(WorkStockBase):
    LOGIN_URL = "https://stockplanconnect.morganstanley.com/cesreg/Home/Home.html#/home"
    LOGIN_POST_URL = "https://stockplanconnect.morganstanley.com/app-bin/cesreg/spc/login/validateLogin"
    SUMMARY_URL = "https://stockplanconnect.morganstanley.com/app-bin/spc/ba/sps/summary?format=json"

    def __init__(self, asset_section, tax_percentage=0.25, **asset_options):
        super(MorganStanleyStockPlanConnect, self).__init__(asset_section, **asset_options)
        self.__tax_percentage = float(tax_percentage)
        summary_data_str = self._session.get(self.SUMMARY_URL).text
        summary_data_str = summary_data_str[summary_data_str.index("{"):]
        self.__summary_data = json.loads(summary_data_str)

    def _establish_session(self, username, password):
        s = requests.Session()
        s.get(self.LOGIN_URL)
        post_data = {"username": username, "password": password}
        result = s.post(self.LOGIN_POST_URL, json=post_data).text
        assert '"success":true' in result, "Result is {}".format(result)
        return s

    def get_summary_value(self, value_name, print_name):
        value_str_raw = self.__summary_data[value_name]
        value = float(value_str_raw[1:].replace(",", ""))
        print_value(value, "{} original (USD)".format(print_name))
        value_ils = convert_usd_to_ils(value) * (1 - self.__tax_percentage)
        print_value(value_ils, "{} final".format(print_name))
        return value_ils

    def _get_exercisable(self):
        return self.get_summary_value("totalMktvalue", "Exercisable")

    def _get_vested(self):
        return 0

    def _get_unvested(self):
        return self.get_summary_value("totalUnvestedvalue", "Unvested")
