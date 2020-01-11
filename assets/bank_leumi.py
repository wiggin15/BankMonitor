# coding=utf-8
import collections
import json
import re
from collections import OrderedDict
from typing import Dict

import requests

from . import stats
from .common import BankBase, HEADERS_USER_AGENT, print_value, AssetValues


class BankLeumi(BankBase):
    LOGIN_URL = "https://hb2.bankleumi.co.il/H/Login.html"
    LOGIN_POST_URL = "https://hb2.bankleumi.co.il/InternalSite/Validate.asp"
    HOME_URL = "https://hb2.bankleumi.co.il/uniquesig0/ebanking/SO/SPA.aspx#/hpsummary"

    def __init__(self, asset_section, print_info=True, **asset_options):
        # type: (str, bool, ...) -> None
        super(BankLeumi, self).__init__(asset_section, **asset_options)
        home_response = self._session.get(self.HOME_URL, headers=HEADERS_USER_AGENT)
        summary_page = home_response.text
        assert u"ברוך הבא, כניסתך האחרונה" in summary_page

        actual_home_url = home_response.url
        unique_sig = actual_home_url.split('/')[3]
        process_request_url = "https://hb2.bankleumi.co.il/{}/ChannelWCF/Broker.svc/ProcessRequest".format(unique_sig)

        private_data_match = re.search(r'var privateData = (.+?);oneTimeRun', summary_page)
        assert private_data_match
        private_data = json.loads(private_data_match.group(1))
        private_data = dict([(key, json.loads(value)) for key, value in private_data.items()])
        session_id = private_data['SO_Signon']['SessionID']

        self.__total_values = collections.defaultdict(float)

        for account_item in private_data['SHEMESHPREMIUM_AccountsItems_hpsummary']['AccountsItems']:
            req_obj = {
                "SessionHeader": {
                    "SessionID": session_id,
                    "FIID": "Leumi"
                },
                "StateName": "HPSummary",
                "ModuleName": "UC_SO_2002_17_GetSummaryData",
                "AccountIndex": account_item['AccountIndex']
            }

            process_request_response = self._session.post(
                process_request_url,
                json={
                    "moduleName": "UC_SO_2002_17_GetSummaryData",
                    "reqObj": json.dumps(req_obj),
                    "version": "V4.0"
                },
                headers=HEADERS_USER_AGENT
            )
            process_request_results = json.loads(process_request_response.text)
            assert process_request_results['ProcessRequestResult'] == 0
            process_request_data = json.loads(process_request_results['jsonResp'])

            if print_info:
                print('Account {} - {}:'.format(account_item['AccountIndex'], account_item['MaskedClientNumber']))
            for account_type_info in process_request_data['TotalPerTypeItems']:
                account_type_name = account_type_info['AccountType'].capitalize()
                if account_type_name == 'Securities':
                    account_type_name = 'Holdings'
                elif account_type_name == 'Cd':
                    account_type_name = 'Deposit'

                account_type_total = account_type_info['TotalPerAccountType']
                if print_info:
                    print_value(account_type_total, account_type_name)
                self.__total_values[account_type_name] = self.__total_values[account_type_name] + account_type_total

    def _establish_session(self, username, password):
        # type: (str, str) -> requests.Session
        s = requests.Session()
        s.get(self.LOGIN_URL, headers=HEADERS_USER_AGENT)
        post_data = {'system': 'test', 'uid': username, 'password': password, 'command': 'login'}
        s.post(self.LOGIN_POST_URL, data=post_data, headers=HEADERS_USER_AGENT)
        return s

    def get_values(self):
        # type: () -> AssetValues
        checking = self.__total_values['Checking']
        holdings = self.__total_values['Holdings']
        deposit = self.__total_values['Deposit']
        return AssetValues(
            OrderedDict([("Checking", checking), ("Holdings", holdings), ("Deposit", deposit)]),
            stats.StatsMapping([stats.StatBank(checking + deposit), stats.StatStockBroker(holdings)])
        )

    def get_total_values(self):
        # type: () -> Dict[str, float]
        return self.__total_values
