#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
import re
import requests
from config import get_config_value
from collections import OrderedDict


def format_value(value_text, print_name=None):
	val = float(value_text.replace(",", ""))
	if print_name is not None:
		print("{}: {:10,.2f}".format(print_name, val))
	return val


class AssetBase(object):
	def __init__(self, username, password):
		self._username = username
		self._password = password
		self._session = self._establish_session(username, password)

	def _establish_session(self, username, password):
		raise NotImplementedError()

	def get_values(self):
		raise NotImplementedError()


class BankOtsar(AssetBase):
	LOGIN_URL = "https://www.fibi-online.co.il/web/otsar"
	HOME_URL = "https://www.fibi-online.co.il/web/TotalPosition.do?SUGBAKA=811&I-OSH-FLAG=1&I-PACHAK-FLAG=1&I-HODAOT-FLAG=1"
	KRANOT_URL = "https://www.fibi-online.co.il/web/Processing?SUGBAKA=021"
	VALUE_RE = """<td nowrap="yes">[0-9/]+</td><td nowrap="yes">(-?[0-9.,]+)</td><td nowrap="yes" dir="(?:rtl)?"><a href="\\./Processing\\?SUGBAKA=%s">"""

	def _establish_session(self, username, password):
		s = requests.Session()
		post_data = {'requestId': 'logon', 'ZIHMIST': username, 'KOD': password}
		s.post(self.LOGIN_URL, data=post_data)
		return s

	def _get_bank_value(self, bank_data, bank_code, print_name=None):
		val_matchobj = re.search(self.VALUE_RE % (bank_code,), bank_data)
		if val_matchobj is None:
			return 0
		val = val_matchobj.group(1)
		return format_value(val, print_name)

	def _get_values_from_main_page(self):
		main_page_html = self._session.get(self.HOME_URL).text
		bank = self._get_bank_value(main_page_html, "077", "OSH")
		deposit = self._get_bank_value(main_page_html, "101", "PIK")
		car = self._get_bank_value(main_page_html, "200", "CAR")
		return bank, deposit, car

	def _get_stock_value(self):
		stock_html = self._session.get(self.KRANOT_URL).text
		NIA = re.search("<td class=\"TITLE\" nowrap>\s*([0-9,.]+)\s*</td>", stock_html)
		NIA = NIA.group(1)
		return format_value(NIA, 'NIA')

	def get_values(self):
		bank, deposit, car = self._get_values_from_main_page()
		stock = self._get_stock_value()
		return OrderedDict([("Bank", bank), ("Deposit", deposit), ("Stock", stock), ("Car", car)])


class BankLeumi(AssetBase):
	LOGIN_URL = "https://hb2.bankleumi.co.il/H/Login.html"
	LOGIN_POST_URL = "https://hb2.bankleumi.co.il/InternalSite/Validate.asp"
	HOME_URL = "https://hb2.bankleumi.co.il/uniquesig0/eBanking/Accounts/PremiumSummaryNew.aspx?p=1"
	CHECKING_RE = ur'<lblCurrentBalanceVal>(.+?)</lblCurrentBalanceVal>'
	HOLDINGS_URL = "https://hb2.bankleumi.co.il/uniquesig0/Trade/net/trade/portf/portfviews3.aspx"
	HOLDINGS_RE = ur'<td nowrap="nowrap" class="positive">&#8362 (.+?)</td>'

	def _establish_session(self, username, password):
		s = requests.Session()
		s.get(self.LOGIN_URL)
		post_data = {'system': 'test', 'uid': username, 'password': password, 'command': 'login'}
		s.post(self.LOGIN_POST_URL, data=post_data)
		return s

	def _get_checking_balance(self):
		summery_page = self._session.get(self.HOME_URL).text
		val_matchobj = re.search(self.CHECKING_RE, summery_page)
		val = val_matchobj.group(1).decode('base64')[4:]
		return format_value(val, 'checking')

	def _get_holdings_balance(self):
		summery_page = self._session.get(self.HOLDINGS_URL).text
		val_matchobj = re.search(self.HOLDINGS_RE, summery_page)
		val = val_matchobj.group(1)
		return format_value(val, 'holdings')

	def get_values(self):
		return OrderedDict([("Checking", self._get_checking_balance()),
						    ("Holdings", self._get_holdings_balance())])


class CardCal(AssetBase):
	CARD_LOGIN_URL = "https://services.cal-online.co.il/card-holders/Screens/AccountManagement/Login.aspx"
	CARD_HOME_URL = "https://services.cal-online.co.il/CARD-HOLDERS/SCREENS/AccountManagement/HomePage.aspx"
	CARD_DETAIL_URL = "https://services.cal-online.co.il/CARD-HOLDERS/SCREENS/AccountManagement/CardDetails.aspx"
	CARD_VALUE_RE = """<span id="%s" class="money"><b>(.*?)</b></span>"""

	def _establish_session(self, username, password):
		s = requests.Session()
		post_data = {"username": username, "password": password}
		s.post(self.CARD_LOGIN_URL, data=post_data)
		return s

	def _get_card_value(self, card_data, card_code, print_name=None):
		val = re.search(self.CARD_VALUE_RE % (card_code,), card_data).group(1)
		return format_value(val, print_name)

	def _get_balance(self, card_code):
		home_data = self._session.get(self.CARD_HOME_URL)
		card_details_queries = re.findall("(\?cardUniqueID=\d+)", home_data.text)
		card_datas = [self._session.get(self.CARD_DETAIL_URL + card_details_query)
					  for card_details_query in card_details_queries]
		return sum(self._get_card_value(card_data.text, card_code) for card_data in card_datas)

	def get_next(self):
		return self._get_balance("lblNextDebitSum")

	def get_values(self):
		card_total = self._get_balance("lblTotalRemainingSum")
		return OrderedDict([("Credit", 0-card_total)])


class CardLeumi(AssetBase):
	TOTAL_RE = ur'<pCreditCardNeg>(.+?)</pCreditCardNeg>'

	def __init__(self, username, password):
		super(CardLeumi, self).__init__(username, password)

	def _establish_session(self, username, password):
		self._bank_instance = BankLeumi(username, password)
		return self._bank_instance._session

	def get_next(self):
		return 0

	def get_values(self):
		summery_page = self._session.get(BankLeumi.HOME_URL).text
		val_matchobj = re.search(self.TOTAL_RE, summery_page)
		if val_matchobj is None:
			return OrderedDict([("Credit", 0)])
		val = val_matchobj.group(1).decode('base64')[5:]
		credit = format_value(val, 'credit')
		return OrderedDict([("Credit", 0-credit)])


def get_asset_checker(asset_type):
	class_name = get_config_value(asset_type, "type")
	user = get_config_value(asset_type, "user")
	password = get_config_value(asset_type, "password")
	if not user or not password:
		raise Exception("{} credentials missing".format(asset_type.capitalize()))
	return globals()[class_name](user, password)


def main():
	all_values = OrderedDict()

	bank_checker = get_asset_checker("bank")
	bank_values = bank_checker.get_values()
	all_values.update(bank_values)

	card_checker = get_asset_checker("card")
	card_values = card_checker.get_values()
	all_values.update(card_values)

	bank_total = sum(bank_values.values())
	card_total = abs(sum(card_values.values()))
	card_next = card_checker.get_next()

	print()
	print("Total Bank: {:10,.2f}".format(bank_total))
	print()
	print("Card: {:,.2f} (next: {:,.2f})".format(card_total, card_next))
	print()
	print("Total: {:10,.2f}".format(bank_total - card_total))
	print()

	return all_values


if __name__ == '__main__':
	main()
	input()
