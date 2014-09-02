from __future__ import print_function
import re
import os
import requests

CARD_USER = ""
CARD_PASSWORD = ""
BANK_USER = ""
BANK_PASSWORD = ""


CARD_LOGIN_URL = "https://services.cal-online.co.il/card-holders/Screens/AccountManagement/Login.aspx"
BANK_LOGIN_URL = "https://www.fibi-online.co.il/web/otsar"
BANK_HOME_URL = "https://www.fibi-online.co.il/web/TotalPosition.do?SUGBAKA=811&I-OSH-FLAG=1&I-PACHAK-FLAG=1&I-HODAOT-FLAG=1"
BANK_KRANOT_URL = "https://www.fibi-online.co.il/web/Processing?SUGBAKA=021"
CARD_HOME_URL = "https://services.cal-online.co.il/CARD-HOLDERS/SCREENS/AccountManagement/HomePage.aspx"
CARD_DETAIL_URL = "https://services.cal-online.co.il/CARD-HOLDERS/SCREENS/AccountManagement/CardDetails.aspx"

CARD_VALUE_RE = """<span id="%s" class="money"><b>(.*?)</b></span>"""
BANK_VALUE_RE = """<td nowrap="yes">[0-9/]+</td><td nowrap="yes">(-?[0-9.,]+)</td><td nowrap="yes" dir="(?:rtl)?"><a href="\\./Processing\\?SUGBAKA=%s">"""

def cal_session(username, password):
	s = requests.Session()
	post_data = {"username": username, "password": password}
	s.post(CARD_LOGIN_URL, data=post_data)
	return s

def otsar_session(username, password):
	s = requests.Session()
	post_data = {'requestId': 'logon', 'ZIHMIST': username, 'KOD': password}
	s.post(BANK_LOGIN_URL, data=post_data)
	return s

def get_bank_value(bank_data, bank_code, print_name=None):
	val_matchobj = re.search(BANK_VALUE_RE % bank_code, bank_data)
	if val_matchobj is None:
		return 0
	val = val_matchobj.group(1)
	val = float(val.replace(",", ""))
	if print_name is not None:
		print(print_name + ":", format(val, "10,.2f"))
	return val

def get_card_value(card_data, card_code, print_name=None):
	val = re.search(CARD_VALUE_RE % card_code, card_data).group(1)
	val = float(val.replace(",", ""))
	if print_name is not None:
		print(print_name + ":", format(val, "9,.2f"))
	return val

def get_bank_values():
	otsar_page_getter = otsar_session(BANK_USER, BANK_PASSWORD)
	bank_data = otsar_page_getter.get(BANK_HOME_URL)
	kranot_html = otsar_page_getter.get(BANK_KRANOT_URL)

	print()
	OSH = get_bank_value(bank_data.text, "077", "OSH")
	PIK = get_bank_value(bank_data.text, "101", "PIK")
	#NIA = get_bank_value(bank_data.text, "021", "NIA")

	# more updated NIA
	NIA = re.search("<td class=\"TITLE\" nowrap>\s*([0-9,.]+)\s*</td>", kranot_html.text)
	NIA = NIA.group(1)
	NIA = float(NIA.replace(",", ""))
	print("NIA:", format(NIA, "9,.2f"))

	CAR = get_bank_value(bank_data.text, "200", "CAR")

	return OSH, PIK, NIA, CAR

def get_card_values():
	cal_page_getter = cal_session(CARD_USER, CARD_PASSWORD)
	home_data = cal_page_getter.get(CARD_HOME_URL)
	card_details_queries = re.findall("(\?cardUniqueID=\d+)", home_data.text)
	card_datas = [cal_page_getter.get(CARD_DETAIL_URL + card_details_query)
	              for card_details_query in card_details_queries]
	card_next = sum(get_card_value(card_data.text, "lblNextDebitSum") for card_data in card_datas)
	card_total = sum(get_card_value(card_data.text, "lblTotalRemainingSum") for card_data in card_datas)
	return card_next, card_total

def main():
	card_next, card_total = get_card_values()

	bank_values = list(get_bank_values())

	bank_total = sum(bank_values)
	print()
	print("Total Bank: %s" % (format(bank_total, "10,.2f"),))
	print()
	print("Card: %s (next: %s)" % (format(card_total, ",.2f"), format(card_next, ",.2f")))
	print()
	print("Total: %s" % (format(bank_total - card_total, "10,.2f"),))
	print()

	return bank_values + [0-card_total]

if __name__ == '__main__':
	main()
	input()
