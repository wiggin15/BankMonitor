from collections import OrderedDict

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as WebDriverOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from . import stats
from .common import BankBase, print_value, AssetValues


# username is in format <id>,<code>

class BankDiscount(BankBase):
    LOGIN_URL = "https://start.telebank.co.il/apollo/core/templates/lobby/masterPage.html?t=P&bank=D&u1=false&multilang=he#/LOGIN_PAGE"
    ACCOUNTS_JSON_URL = "https://start.telebank.co.il/Titan/gatewayAPI/userAccountsData"
    BALANCE_JSON_URL = "https://start.telebank.co.il/Titan/gatewayAPI/accountDetails/{}"
    STOCK_JSON_URL = "https://start.telebank.co.il/Titan/gatewayAPI/securities/portfolioInfo/currentSecuritiesPortfolio"

    def _wait_for_id(self, html_id):
        indicator = EC.presence_of_element_located((By.ID, html_id))
        WebDriverWait(self.selenium, 180).until(indicator)

    def _establish_session(self, username, password):
        # type: (str, str) -> requests.Session
        uid, code = username.split(",")
        options = WebDriverOptions()
        options.headless = True
        self.selenium = webdriver.Firefox(options=options)
        try:
            self.selenium.get(self.LOGIN_URL)
            self._wait_for_id("tzId")
            self.selenium.find_element_by_id("tzId").send_keys(uid)
            self.selenium.find_element_by_id("tzPassword").send_keys(password)
            self.selenium.find_element_by_id("aidnum").send_keys(code)
            self.selenium.find_element_by_class_name("sendBtn").click()
            self._wait_for_id("balance-box-homepage")

            session = requests.Session()
            for cookie in self.selenium.get_cookies():
                session.cookies.set(cookie['name'], cookie['value'])
        finally:
            self.selenium.quit()

        return session

    def get_values(self):
        # type: () -> AssetValues
        accounts_data = self._session.get(self.ACCOUNTS_JSON_URL).json()
        account_numbers = [account['FormatAccountID'] for account in accounts_data['UserAccountsData']['UserAccounts']]
        bank = 0
        stock = 0
        for account_number in account_numbers:
            bank += self._session.get(self.BALANCE_JSON_URL.format(account_number)).json()['AccountDetails'][
                'AccountBalance']
            stock += self._session.post(self.STOCK_JSON_URL, json={"AccountNumber": account_number}).json()[
                'CurrentSecuritiesPortfolio']['PortfolioValue']
        print_value(bank, "OSH")
        print_value(stock, "NIA")
        return AssetValues(
            OrderedDict([("Bank", bank), ("Deposit", 0), ("Stock", stock), ("Car", 0)]),
            stats.StatsMapping([stats.StatBank(bank), stats.StatStockBroker(stock)])
        )
