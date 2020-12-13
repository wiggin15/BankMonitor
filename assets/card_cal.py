import re
import requests
from .common import CardBase, format_value, print_value

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as WebDriverOptions
import time

class CardCal(CardBase):
    CARD_LOGIN_URL = "https://services.cal-online.co.il/card-holders/Screens/AccountManagement/Login.aspx"
    CARD_HOME_URL = "https://services.cal-online.co.il/CARD-HOLDERS/SCREENS/AccountManagement/HomePage.aspx"
    CARD_DETAIL_URL = "https://services.cal-online.co.il/CARD-HOLDERS/SCREENS/AccountManagement/CardDetails.aspx"
    CARD_VALUE_RE = """<span id="%s" class="money"><b>(.*?)</b></span>"""

    def _wait_for_id(self, html_id):
        indicator = EC.presence_of_element_located((By.ID, html_id))
        WebDriverWait(self.selenium, 10).until(indicator)

    def _wait_for_name(self, html_name):
        indicator = EC.presence_of_element_located((By.NAME, html_name))
        WebDriverWait(self.selenium, 10).until(indicator)

    def _establish_session(self, username, password):
        options = WebDriverOptions()
        options.headless = True
        self.selenium = webdriver.Firefox(options=options)
        try:
            self.selenium.get(self.CARD_LOGIN_URL)
            self._wait_for_id("calconnectIframe")
            self.selenium.switch_to.frame(self.selenium.find_element_by_id("calconnectIframe"))
            self._wait_for_id("mat-input-0")
            # switch to login by username/password
            self.selenium.find_element_by_css_selector('a.mat-tab-link:nth-child(2)').click()
            self._wait_for_id("mat-input-2")
            self.selenium.find_element_by_id("mat-input-2").send_keys(username)
            self.selenium.find_element_by_id("mat-input-3").send_keys(password)
            self.selenium.find_element_by_css_selector('form button[type="submit"]').submit()
            # wait until submission actually goes through and we get a new page
            self.selenium.switch_to.default_content()
            self._wait_for_id("tabsContainer")

            session = requests.Session()
            for cookie in self.selenium.get_cookies():
                session.cookies.set(cookie['name'], cookie['value'])
        finally:
            self.selenium.quit()

        return session

    def _get_card_value(self, card_data, card_code, print_name=None):
        val = re.search(self.CARD_VALUE_RE % (card_code,), card_data).group(1)
        return format_value(val, print_name)

    def _get_balance(self, card_code):
        home_data = self._session.get(self.CARD_HOME_URL)
        card_details_queries = re.findall("(\?cardUniqueID=\d+)", home_data.text)
        card_datas = [self._session.get(self.CARD_DETAIL_URL + card_details_query)
                      for card_details_query in card_details_queries]
        return sum(self._get_card_value(card_data.text, card_code) for card_data in card_datas)

    def get_credit(self):
        card_total = self._get_balance("lblTotalRemainingSum")
        print_value(0 - card_total, "Credit")
        return 0 - card_total

    def get_next(self):
        return self._get_balance("lblNextDebitSum")
