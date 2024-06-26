from __future__ import print_function
import re
import requests
from collections import OrderedDict
from .common import BankBase, format_value

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import time
import os

headers = {"User-Agent": "Mozilla/5.0"}


class BankBeinleumi(BankBase):
    HOME_URL = "https://online.fibi.co.il/wps/myportal/FibiMenu/Online"
    BALANCE_URL = "https://online.fibi.co.il/wps/myportal/FibiMenu/Online/OnAccountMngment/OnBalanceTrans/PrivateAccountFlow"
    STOCK_URL = "https://online.fibi.co.il/wps/myportal/FibiMenu/Online/OnCapitalMarket/OnMyportfolio/AuthSecuritiesPrtfMyPFEquities"
    BALANCE_PATTERN = """<span class="main_balance[^>]*>\s+([^<]+)</span>"""
    STOCK_PATTERN = '"fibi_amount">\s*(\S+?)\s*<'

    def _wait_for_id(self, html_id):
        indicator = EC.presence_of_element_located((By.ID, html_id))
        WebDriverWait(self.selenium, 10).until(indicator)

    def _establish_session(self, username, password):
        os.environ["DISPLAY"] = ":1"
        self.selenium = webdriver.Firefox()
        self.selenium.get("https://online.fibi.co.il/")
        self._wait_for_id("LoginIframeTag")
        self.selenium.switch_to.frame(self.selenium.find_element(By.ID, "LoginIframeTag"))
        self._wait_for_id("username")
        self.selenium.find_element(By.ID, "username").send_keys(username)
        self.selenium.find_element(By.ID, "password").send_keys(password)
        self.selenium.find_element(By.ID, "loginForm").submit()
        # wait until submission actually goes through and we get a new page
        self.selenium.switch_to.default_content()
        self._wait_for_id("rightsideBar")

        session = requests.Session()
        for cookie in self.selenium.get_cookies():
            session.cookies.set(cookie['name'], cookie['value'])

        self.selenium.quit()

        return session

    def _get_accounts(self):
        main_html = self._session.get(self.HOME_URL, headers=headers).text
        return re.findall('option value="([^"]+)"', main_html)

    def _switch_account(self, account):
        main_html = self._session.get(self.HOME_URL, headers=headers).text
        base_href = re.search('<base href="([^"]+)">', main_html).group(1)
        form_action = re.search('<form method="post" action="([^"]+)" name="refreshPortletForm" id="refreshPortletForm">', main_html).group(1)
        data = dict(PortletForm_ACTION_NAME="changeAccount", portal_current_account=account)
        self._session.post(base_href + form_action, data=data, headers=headers)

    def _get_values_from_main_page(self):
        main_html = self._session.get(self.BALANCE_URL, headers=headers).text
        match_obj = re.search(self.BALANCE_PATTERN, main_html, re.DOTALL)
        if match_obj is None:
            return 0
        OSH = match_obj.group(1)
        return format_value(OSH)

    def _get_stock_value(self):
        stock_html = self._session.get(self.STOCK_URL, headers=headers).text
        match_obj = re.search(self.STOCK_PATTERN, stock_html)
        if match_obj is None:
            return 0
        NIA = match_obj.group(1)
        return format_value(NIA)

    def get_values(self):
        bank = 0
        stock = 0
        for account in self._get_accounts():
            self._switch_account(account)
            bank += self._get_values_from_main_page()
            stock += self._get_stock_value()
        print("OSH: {:10,.2f}".format(bank))
        print("NIA: {:10,.2f}".format(stock))
        return OrderedDict([("Bank", bank), ("Deposit", 0), ("Stock", stock), ("Car", 0)])
