#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
import time
import os
import bank
import web
from config import WEBSERVER_IP_ADDR, WEBSERVER_PORT, WEBSERVER_FILE_PATH
from collections import OrderedDict

def update():
	date = time.strftime("%d/%m/%Y")
	values = OrderedDict([("Date", date)])
	values.update(bank.main())

	new_content = ','.join([str(x) for x in values.values()]) + "\r\n"
	if not os.path.isfile(WEBSERVER_FILE_PATH):
		new_content = ','.join(values.keys()) + "\r\n" + new_content
	new_content.encode("ascii")
	with open(WEBSERVER_FILE_PATH, "ab+") as f:
		f.write(new_content)

def open_browser():
	import webbrowser
	webbrowser.open("http://{}:{}".format(WEBSERVER_IP_ADDR, WEBSERVER_PORT))

def main():
	update()
	print("Starting webserver...")
	import threading
	threading.Timer(2, open_browser).start()
	web.main()

if __name__ == '__main__':
	main()
