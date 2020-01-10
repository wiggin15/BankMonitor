import json
import re

import requests

from .common import WorkStockBase, format_value, HEADERS_USER_AGENT


class StockFidelityNetBenefits(WorkStockBase):
    LOGIN_URL = "https://nb.fidelity.com/public/nb/default/home"
    SENSOR_DATA_URL = "https://nb.fidelity.com/_bm/_data"
    PRE_LOGIN_URL = "https://nb.fidelity.com/public/nb/api/prelogin/default"
    LOGIN_INIT_URL = "https://login.fidelity.com/ftgw/Fas/Fidelity/PWI/Login/Init/dj.chf.ra"
    LOGIN_POST_URL = "https://login.fidelity.com/ftgw/Fas/Fidelity/PWI/Login/Response/dj.chf.ra/"
    SUMMARY_URL = "https://netbenefitsww.fidelity.com/mybenefitsww/stockplans/navigation/PlanSummary"

    def _establish_session(self, username, password):
        # type: (str, str) -> requests.Session
        s = requests.Session()
        s.get(self.LOGIN_URL, headers=HEADERS_USER_AGENT)

        # Copied from a live browser session. No idea what it contains
        post_data = {
            "sensor_data": "7a74G7m23Vrp0o5c9845726.78-6,2,-36,-495,Mozilla/9.8 (Windows NT 52.1; Win85; x70; rv:41.5) Gecko/48239676 Firefox/37.9,uaend,2921,01495853,en-US,Gecko,8,2,5,0,913276,8781053,2562,2335,6135,1144,9059,041,6837,,cpen:5,i3:5,dm:4,cwen:7,non:1,opc:1,fc:6,sc:0,wrc:2,isc:14,vib:5,bat:5,x32:9,x76:9,8404,2.214685409657,275351673132.4,loc:-0,3,-12,-058,do_en,dm_en,t_dis-6,2,-36,-490,-3,7,-00,-915,-8,4,-84,-526,-0,9,-09,-274,-2,1,-46,-018,-3,3,-41,-260,-7,4,-23,-620,-1,8,-75,-689,-6,2,-36,-498,-3,7,-00,-925,https://nb.fidelity.com/public/nb/default/home-0,9,-09,-279,8,3,5,5,1,9,1,9,8,4456244529067,-028464,21051,4,8,5548,2,5,11,4,8,AED44CAC14CBA4C4D6860B9C96762BB88113B6CC405042811D3BFC649319A051~-6~Jy5+Psrqp/Dbx159mM2fAwUXOrro6lddHa9LsYOTyI8=~-6~-3,3100,-3,-4,72064578-7,4,-23,-627,9,1-5,0,-89,-324,-2-5,0,-89,-337,0,6,2,1,0,7,2-6,2,-36,-09,-6-2,1,-58,-93,41-3,7,-00,-929,62610026-7,4,-23,-639,39332-9,5,-69,-611,;6;-1;0"
        }
        sensor_response = s.post(self.SENSOR_DATA_URL, json=post_data, headers=HEADERS_USER_AGENT)
        sensor_response_data = json.loads(sensor_response.text)
        assert sensor_response_data.get("success")

        s.get(self.PRE_LOGIN_URL, headers=HEADERS_USER_AGENT)
        s.get(self.LOGIN_INIT_URL, headers=HEADERS_USER_AGENT)

        post_data = {
            "username": username,
            "password": password,
            "SavedIdInd": "N",
        }
        login_response = s.post(self.LOGIN_POST_URL, data=post_data, headers=HEADERS_USER_AGENT)
        login_response_data = json.loads(login_response.text)
        assert login_response_data.get("status", {}).get("result", "") == "success"

        return s

    def _get_exercisable(self):
        # type: () -> float
        summary_data_str = self._session.get(self.SUMMARY_URL).text
        match = re.search("""<sup class="dollar">.+?</sup>(.+?)<span class="currency">""", summary_data_str)
        return format_value(match.group(1), "Total")

    def _get_vested(self):
        # type: () -> float
        return 0

    def _get_unvested(self):
        # type: () -> float
        return 0
