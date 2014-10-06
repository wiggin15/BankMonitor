#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
import time
import datetime
import sys
from bank_csv import update

def wait_until_time(hour, minute):
	print("Sleeping until {:02d}:{:02d}".format(hour, minute))
	now = datetime.datetime.now()
	next_time = datetime.datetime(now.year, now.month, now.day, hour, minute)
	if now.hour > hour or (now.hour == hour and now.minute >= minute):
		# it's already past the time, so update tomorrow
		next_time += datetime.timedelta(days=1)
	while True:
		now = datetime.datetime.now()
		remaining = (next_time - now).total_seconds()
		if remaining < 0:
			sys.stdout.write("\r" + " " * 80 + "\r")
			sys.stdout.flush()
			return
		# print remaining nicely
		sys.stdout.write("Time remaining: ")
		sys.stdout.write(time.strftime('%H:%M', time.gmtime(remaining)))
		sys.stdout.flush()
		time.sleep(min(60, remaining))
		sys.stdout.write("\r")
		sys.stdout.flush()

def main():
	while True:
		wait_until_time(20, 0)
		print("-" * 20)
		print("updating", time.strftime("%d/%m/%y"))
		update()

if __name__ == '__main__':
	main()
