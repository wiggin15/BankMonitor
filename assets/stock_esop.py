from __future__ import print_function
import json
import requests
from datetime import datetime
from assets.common import StockBrokerBase, get_stock_value, convert_usd_to_ils, print_value


class StockEsop(StockBrokerBase):
    LOGIN_URL = "https://www.capital-m.co.il/C-MClient/j_security_check"
    SERVLET_URL = "https://www.capital-m.co.il/C-MClient/theme/js/gwt/optionsPlanDetails/gwtservlet"
    PLAN_OBJECT_DATA_LENGTH = 49

    def __init__(self, asset_section, gain_tax_percentage=0.28, income_tax_percentage=0.62, **asset_options):
        super(StockEsop, self).__init__(asset_section, **asset_options)
        self.__gain_tax_percentage = float(gain_tax_percentage)
        self.__income_tax_percentage = float(income_tax_percentage)
        self.__plan_data = self.__get_plan_details()

    def _establish_session(self, username, password):
        s = requests.Session()
        post_data = {"j_username": username, "j_password": password}
        s.post(self.LOGIN_URL, data=post_data)
        return s

    def __get_plan_details(self):
        # GWT RPC is really bad :(
        # Here are some docs: https://docs.google.com/document/d/1eG0YocsYYbNAtivkLtcaiEE5IOF5u4LUol8-LL0TIKU/edit

        # This is a breakdown of the request, for future generations:
        # 5| # Protocol version
        # 0| # No flags
        # 9| # 9 strings in the following table (access is 1-based)
        #
        # https://www.capital-m.co.il/C-MClient/theme/js/gwt/optionsPlanDetails/|
        # AC2E99386390CA9EE9D422978B9DE88C|
        # cmr.client.plan.services.OptionsPlanDetailsService|
        # getSpecificOptionsPlanDetailData|
        # java.util.Date/1659716317|
        # I|
        # J|
        # java.lang.String/2004016611|
        # ********| # Username
        #
        # 1|2|3|4| # Call a method
        # 4| # The method has 4 parameters
        # 5|6|7|8| # Parameter types - Date, int, long, String
        # 5|4085046400|1503238553600| # Start of current day, as the low int and high int
        # 0| # Int with value 0
        # 0|0| # Long with value 0 as two ints
        # 9| # String with username from string table
        timestamp = int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() * 1000)
        timestamp_high = timestamp & 0xffffffff00000000
        timestamp_low = timestamp & 0xffffffff
        post_data = "5|0|9|https://www.capital-m.co.il/C-MClient/theme/js/gwt/optionsPlanDetails/|AC2E99386390CA9EE9D422978B9DE88C|cmr.client.plan.services.OptionsPlanDetailsService|getSpecificOptionsPlanDetailData|java.util.Date/1659716317|I|J|java.lang.String/2004016611|{}|1|2|3|4|4|5|6|7|8|5|{}|{}|0|0|0|9|" \
            .format(self._username, timestamp_high, timestamp_low)

        headers = {"Content-Type": "text/x-gwt-rpc; charset=UTF-8",
                   "X-GWT-Module-Base": "https://www.capital-m.co.il/C-MClient/theme/js/gwt/optionsPlanDetails/",
                   "X-GWT-Permutation": "1781C0258DE0C55897A4212CAA3FC838"}

        result = self._session.post(self.SERVLET_URL, data=post_data, headers=headers).text
        assert result.startswith("//OK"), "Result is {}".format(result)

        result_json = json.loads(result[4:])
        assert isinstance(result_json, list)
        result_json.reverse()
        assert result_json[0] == 5, "Protocol version is {}".format(result_json[0])

        return self.__parse_plan_details_object(result_json[3:], result_json[2])

    def __parse_plan_details_object(self, object_data, string_table):
        assert object_data[0] == 1
        assert string_table[object_data[0] - 1] == "cmr.client.main.models.MainContentData/859749487", \
            "Unknown response object {}".format(string_table[object_data[0] - 1])

        # Look for a member of an array type
        assert object_data[10] == 4
        assert string_table[object_data[10] - 1] == "java.util.ArrayList/3821976829"
        plans_count = object_data[11]

        array_data = [object_data[i:i + self.PLAN_OBJECT_DATA_LENGTH]
                      for i in range(12, 12 + plans_count * self.PLAN_OBJECT_DATA_LENGTH, self.PLAN_OBJECT_DATA_LENGTH)]
        return [self.__parse_single_plan_object(x, string_table) for x in array_data]

    def __parse_single_plan_object(self, object_data, string_table):
        assert object_data[0] == 5
        assert string_table[object_data[0] - 1] == "cmr.client.main.models.OptionsPlanDetailDataWrapper/457096247", \
            "Unknown plan details object {}".format(string_table[object_data[0] - 1])
        assert len(object_data) == self.PLAN_OBJECT_DATA_LENGTH

        buy_price = object_data[8]

        assert object_data[14] == 7
        assert string_table[object_data[14] - 1] == "java.sql.Timestamp/1769758459", \
            "Unknown timestamp object {}".format(string_table[object_data[14] - 1])
        lockup_time_end_low = object_data[15]
        lockup_time_end_high = object_data[16]
        lockup_time_end = datetime.utcfromtimestamp((lockup_time_end_low + lockup_time_end_high) / 1000)

        held_shares = object_data[35]
        exercisable_shares = held_shares if datetime.utcnow() > lockup_time_end else 0
        vested_shares = held_shares - exercisable_shares
        unvested_shares = object_data[41]

        stock_name = string_table[object_data[33] - 1]
        current_stock_value = get_stock_value(stock_name)

        print("Found {} exercisable, {} vested and {} unvested shares, with price {} (current price {})"
              .format(exercisable_shares, vested_shares, unvested_shares, buy_price, current_stock_value))

        net_share_value = convert_usd_to_ils(current_stock_value -
                                             (buy_price * self.__income_tax_percentage) -
                                             ((current_stock_value - buy_price) * self.__gain_tax_percentage))

        return {"Exercisable": exercisable_shares * net_share_value,
                "Vested": vested_shares * net_share_value,
                "Unvested": unvested_shares * net_share_value}

    def __get_total_value(self, value_name):
        result = sum([x[value_name] for x in self.__plan_data])
        print_value(result, value_name)
        return result

    def get_exercisable(self):
        return self.__get_total_value("Exercisable")

    def get_vested(self):
        return self.__get_total_value("Vested")

    def get_unvested(self):
        return self.__get_total_value("Unvested")
