import json
import requests

from assets.common import CommodityBase, print_value


class Cryptocurrency(CommodityBase):
    TARGET_CURRENCY = "ILS"

    def __init__(self, asset_section, symbol=None, **asset_options):
        super(Cryptocurrency, self).__init__(asset_section, **asset_options)
        self.__symbol = symbol
        if not self.__symbol:
            raise Exception("{} symbol missing".format(asset_section.capitalize()))

    def _get_value(self):
        url = "https://min-api.cryptocompare.com/data/price?fsym={}&tsyms={}".format(self.__symbol,
                                                                                     self.TARGET_CURRENCY)
        api_result = requests.get(url).text
        api_data = json.loads(api_result)
        currency_value = api_data[self.TARGET_CURRENCY]
        total_value = self._amount * currency_value
        print_value(total_value, "Value")
        return total_value
