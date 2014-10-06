#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
import time
import os
import bank
import web
from config import WEBSERVER_IP_ADDR, WEBSERVER_PORT, WEBSERVER_FILE_PATH

def update():
	date = time.strftime("%d/%m/%Y")
	all_values, all_names = bank.main()
	all_values.insert(0, date)
	all_names.insert(0, "Date")

	new_content = ','.join([str(x) for x in all_values]) + "\r\n"
	if (not os.path.isfile(WEBSERVER_FILE_PATH)):
		new_content = ','.join(all_names) + "\r\n" + new_content
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
