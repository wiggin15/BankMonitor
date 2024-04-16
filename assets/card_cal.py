import requests
from .common import CardBase, print_value

HEADERS = {"X-Site-ID": "09031987-273E-2311-906C-8AF85B17C8D9", "User-Agent": "Mozilla/5.0 ()"}

class CardCal(CardBase):
    API_LOGIN_URL = "https://connect.cal-online.co.il/col-rest/calconnect/authentication/login"
    API_DETAILS_URL = "https://api.cal-online.co.il/Transactions/api/financeDashboard/getBigNumberAndDetails"
    API_INIT_URL = "https://api.cal-online.co.il/Authentication/api/account/init"

    def _establish_session(self, username, password):
        session = requests.Session()

        login_data = {"username": username, "password": password, "recaptcha": ""}
        response = session.post(self.API_LOGIN_URL, json=login_data, headers=HEADERS)
        token = response.json()['token']

        session.headers = {"Authorization": f"CALAuthScheme {token}", **HEADERS}

        return session

    def get_credit(self):
        response = self._session.post(self.API_INIT_URL, json={"tokenGuid": ""})
        data = response.json()
        bank_id = data['result']['bankAccounts'][0]['bankAccountUniqueId']

        response = self._session.post(self.API_DETAILS_URL, json={"bankAccountUniqueId": bank_id})
        data = response.json()
        total_debit = data['result']['bigNumbers'][0]['totalDebits'][0]['totalDebit']
        print_value(-total_debit, "Credit")
        return -total_debit
