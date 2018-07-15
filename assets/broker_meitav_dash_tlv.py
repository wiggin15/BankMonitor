import json
from collections import OrderedDict

import requests
from requests.auth import AuthBase

from assets import stats
from assets.common import AuthenticatedAssetBase, print_value


class BrokerMeitavDashTlv(AuthenticatedAssetBase):
    LOGIN_URL = "https://sparkmeitav.ordernet.co.il/#/auth"
    AUTH_URL = "https://sparkmeitav.ordernet.co.il/api/Auth/Authenticate"
    GET_DETAILS_URL = "https://sparkmeitav.ordernet.co.il/api/Account/GetAccountSecurities?accountKey=ACC_000-"

    def __init__(self, asset_section, account_id=None, **asset_options):
        self.__account_id = account_id
        if not self.__account_id:
            raise Exception("{} account ID is missing".format(asset_section.capitalize()))
        super(BrokerMeitavDashTlv, self).__init__(asset_section, **asset_options)

    def _establish_session(self, username, password):
        s = requests.Session()
        s.get(self.LOGIN_URL)
        post_data = {'username': username, 'password': password}
        response_raw = s.post(self.AUTH_URL, json=post_data).text
        response = json.loads(response_raw)
        assert response.get('a') == 'Success'
        auth_token = response.get('l')
        self.__auth = BearerAuth(auth_token)
        return s

    def get_values(self, stats_dict):
        details_raw = self._session.get(self.GET_DETAILS_URL + self.__account_id, auth=self.__auth).text
        details = json.loads(details_raw)
        total = details.get('a').get('a')
        print_value(total, 'Total')
        stats_dict.get_stat(stats.StatType.STAT_STOCK_BROKER).add(total)
        return OrderedDict([('Total', total)])


class BearerAuth(AuthBase):

    def __init__(self, auth_token):
        self.__auth_token = auth_token

    def __call__(self, r):
        r.headers['Authorization'] = "Bearer " + self.__auth_token
        return r
