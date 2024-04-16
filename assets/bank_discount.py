import re
import requests
from collections import OrderedDict
from .common import BankBase, format_value, HEADERS_USER_AGENT
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as WebDriverOptions

# username is in format <id>,<code>

class BankDiscount(BankBase):
    LOGIN_URL = "https://start.telebank.co.il/login/"
    ACCOUNTS_JSON_URL = "https://start.telebank.co.il/Titan/gatewayAPI/userAccountsData"
    BALANCE_JSON_URL = "https://start.telebank.co.il/Titan/gatewayAPI/accountDetails/{}"
    CREDIT_JSON_URL = "https://start.telebank.co.il/Titan/gatewayAPI/creditCards/totalDebitTransactions/{}"
    STOCK_JSON_URL = "https://start.telebank.co.il/Titan/gatewayAPI/securities/portfolioInfo/currentSecuritiesPortfolio"

    def _wait_for_id(self, html_id):
        indicator = EC.presence_of_element_located((By.ID, html_id))
        WebDriverWait(self.selenium, 180).until(indicator)

    def _establish_session(self, username, password):
        uid, code = username.split(",")
        options = WebDriverOptions()
        options.headless = True
        self.selenium = webdriver.Firefox(options=options)
        try:
            self.selenium.get(self.LOGIN_URL)
            self._wait_for_id("tzId")
            self.selenium.find_element(By.ID, "tzId").send_keys(uid)
            self.selenium.find_element(By.ID, "tzPassword").send_keys(password)
            self.selenium.find_element(By.ID, "aidnum").send_keys(code)
            elem = self.selenium.find_element(By.ID, "full_page_loader")
            self.selenium.execute_script('arguments[0].style.display = "none"', elem)
            self.selenium.find_element(By.CLASS_NAME, "sendBtn").click()
            self._wait_for_id("balance-box-homepage")

            session = requests.Session()
            for cookie in self.selenium.get_cookies():
                session.cookies.set(cookie['name'], cookie['value'])
        finally:
            self.selenium.quit()

        session.headers = HEADERS_USER_AGENT

        return session

    def get_values(self):
        accounts_data = self._session.get(self.ACCOUNTS_JSON_URL).json()
        account_numbers = [account['FormatAccountID'] for account in accounts_data['UserAccountsData']['UserAccounts']]
        bank = 0
        stock = 0
        credit = 0
        for account_number in account_numbers:
            bank += self._session.get(self.BALANCE_JSON_URL.format(account_number)).json()['AccountDetails']['AccountBalance']
            credit += self._session.get(self.CREDIT_JSON_URL.format(account_number)).json()['TotalDebitTransactions']['TotalsBlock']['NISExternalCardsEstimatedTotalDebit']
            stock += self._session.post(self.STOCK_JSON_URL, json={"AccountNumber": account_number}).json()['CurrentSecuritiesPortfolio']['PortfolioValue']
        print("OSH: {:10,.2f}".format(bank))
        print("NIA: {:10,.2f}".format(stock))
        return OrderedDict([("Bank", bank), ("Deposit", 0), ("Stock", stock), ("Car", 0)])
