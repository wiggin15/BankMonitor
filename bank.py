#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
import re
import requests
from config import get_config_value, get_config_bool



def format_value(value_text, print_name=None):
	val = float(value_text.replace(",", ""))
	if print_name is not None:
		print("{}: {:10,.2f}".format(print_name, val))
	return val

class BankBase(object):
	def __init__(self, username, password):
		self._username = username
		self._password = password
		self._session = self._establish_session(username, password)

	def _establish_session(self, username, password):
		raise NotImplementedError()

	def get_checking_balance(self):
		raise NotImplementedError()

	def get_deposit_balance(self):
		raise NotImplementedError()

	def get_holdings_balance(self):
		raise NotImplementedError()

	def get_car_loan_balance(self):
		raise NotImplementedError()



class BankOtsar(BankBase):
	LOGIN_URL = "https://www.fibi-online.co.il/web/otsar"
	HOME_URL = "https://www.fibi-online.co.il/web/TotalPosition.do?SUGBAKA=811&I-OSH-FLAG=1&I-PACHAK-FLAG=1&I-HODAOT-FLAG=1"
	KRANOT_URL = "https://www.fibi-online.co.il/web/Processing?SUGBAKA=021"
	VALUE_RE = """<td nowrap="yes">[0-9/]+</td><td nowrap="yes">(-?[0-9.,]+)</td><td nowrap="yes" dir="(?:rtl)?"><a href="\\./Processing\\?SUGBAKA=%s">"""

	def _establish_session(self, username, password):
		s = requests.Session()
		post_data = {'requestId': 'logon', 'ZIHMIST': username, 'KOD': password}
		s.post(self.LOGIN_URL, data=post_data)
		return s

	def __get_bank_value(self, bank_data, bank_code, print_name=None):
		val_matchobj = re.search(self.VALUE_RE % (bank_code,), bank_data)
		if val_matchobj is None:
			return 0
		val = val_matchobj.group(1)
		return format_value(val, print_name)

	def __get_bank_data(self):
		return self._session.get(self.HOME_URL).text

	def get_checking_balance(self):
		return self.__get_bank_value(self.__get_bank_data(), "077", "OSH")

	def get_deposit_balance(self):
		return self.__get_bank_value(self.__get_bank_data(), "101", "PIK")

	def get_holdings_balance(self):
		kranot_html = self._session.get(self.KRANOT_URL).text
		NIA = re.search("<td class=\"TITLE\" nowrap>\s*([0-9,.]+)\s*</td>", kranot_html)
		NIA = NIA.group(1)
		return format_value(NIA, 'NIA')

	def get_car_loan_balance(self):
		return self.__get_bank_value(self.__get_bank_data(), "200", "CAR")


class BankLeumi(BankBase):
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

	def get_checking_balance(self):
		summery_page = self._session.get(self.HOME_URL).text
		val_matchobj = re.search(self.CHECKING_RE, summery_page)
		val = val_matchobj.group(1).decode('base64')[4:]
		return format_value(val, 'checking')

	def get_holdings_balance(self):
		summery_page = self._session.get(self.HOLDINGS_URL).text
		val_matchobj = re.search(self.HOLDINGS_RE, summery_page)
		val = val_matchobj.group(1)
		return format_value(val, 'holdings')
	


class CardBase(object):
	def __init__(self, username, password):
		self._username = username
		self._password = password
		self._session = self._establish_session(username, password)

	def _establish_session(self, username, password):
		raise NotImplementedError()

	def get_balance(self):
		raise NotImplementedError()


class CardCal(CardBase):
	CARD_LOGIN_URL = "https://services.cal-online.co.il/card-holders/Screens/AccountManagement/Login.aspx"
	CARD_HOME_URL = "https://services.cal-online.co.il/CARD-HOLDERS/SCREENS/AccountManagement/HomePage.aspx"
	CARD_DETAIL_URL = "https://services.cal-online.co.il/CARD-HOLDERS/SCREENS/AccountManagement/CardDetails.aspx"
	CARD_VALUE_RE = """<span id="%s" class="money"><b>(.*?)</b></span>"""

	def _establish_session(self, username, password):
		s = requests.Session()
		post_data = {"username": username, "password": password}
		s.post(self.CARD_LOGIN_URL, data=post_data)
		return s

	def __get_card_value(self, card_data, card_code, print_name=None):
		val = re.search(self.CARD_VALUE_RE % (card_code,), card_data).group(1)
		val = float(val.replace(",", ""))
		return format_value(val, print_name)

	def get_balance(self):
		home_data = self._session.get(self.CARD_HOME_URL)
		card_details_queries = re.findall("(\?cardUniqueID=\d+)", home_data.text)
		card_datas = [self._session.get(self.CARD_DETAIL_URL + card_details_query)
					  for card_details_query in card_details_queries]
		card_next = sum(get_card_value(card_data.text, "lblNextDebitSum") for card_data in card_datas)
		card_total = sum(get_card_value(card_data.text, "lblTotalRemainingSum") for card_data in card_datas)
		return card_next, card_total


class CardLeumi(CardBase):
	TOTAL_RE = ur'<pCreditCardNeg>(.+?)</pCreditCardNeg>'

	def __init__(self, username, password):
		super(CardLeumi, self).__init__(username, password)

	def _establish_session(self, username, password):
		self._bank_instance = BankLeumi(username, password)
		return self._bank_instance._session

	def __get_card_value(self, card_data, card_code, print_name=None):
		val = re.search(self.CARD_VALUE_RE % (card_code,), card_data).group(1)
		val = float(val.replace(",", ""))
		return format_value(val, print_name)

	def get_balance(self):
		summery_page = self._session.get(BankLeumi.HOME_URL).text
		val_matchobj = re.search(self.TOTAL_RE, summery_page)
		if val_matchobj is None:
			return 0, 0
		val = val_matchobj.group(1).decode('base64')[5:]
		return 0, format_value(val, 'credit')


def main():
	all_values = []
	all_names = []

	bank_class_name = get_config_value("bank", "type")
	bank_user = get_config_value("bank", "user")
	if not bank_user:
		raise Exception("You must provide a user name for the bank site")
	bank_password = get_config_value("bank", "password")
	if not bank_password:
		raise Exception("You must provide a password for the bank site")
	
	bank_checker = globals()[bank_class_name](bank_user, bank_password)
	
	if get_config_bool("bank", "get_checking_balance"):
		all_values.append(bank_checker.get_checking_balance())
		all_names.append("Checking")
	if get_config_bool("bank", "get_deposit_balance"):
		all_values.append(bank_checker.get_deposit_balance())
		all_names.append("Deposit")
	if get_config_bool("bank", "get_holdings_balance"):
		all_values.append(bank_checker.get_holdings_balance())
		all_names.append("Holdings")
	if get_config_bool("bank", "get_car_loan_balance"):
		all_values.append(bank_checker.get_car_loan_balance())
		all_names.append("Car")
	
	bank_total = sum(all_values)
	
	card_class_name = get_config_value("card", "type")
	card_user = get_config_value("card", "user")
	if not card_user:
		raise Exception("You must provide a user name for the credit card site")
	card_password = get_config_value("card", "password")
	if not card_password:
		raise Exception("You must provide a password for the credit card site")
	
	card_checker = globals()[card_class_name](card_user, card_password)
	card_next, card_total = card_checker.get_balance()
	all_values.append(0-card_total)
	all_names.append("Credit")

	print()
	print("Total Bank: {:10,.2f}".format(bank_total))
	print()
	print("Card: {:,.2f} (next: {:,.2f})".format(card_total, card_next))
	print()
	print("Total: {:10,.2f}".format(bank_total - card_total))
	print()

	return all_values, all_names

if __name__ == '__main__':
	main()
	input()
