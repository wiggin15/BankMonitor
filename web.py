import cherrypy
import os
import sys

import json
import datetime
from collections import OrderedDict

IP_ADDR = "127.0.0.1"
PORT = 7070

def get_path():
	if sys.platform == "win32":
		return os.path.expandvars(r"%userprofile%\Google Drive\logs\bank.csv")
	elif sys.platform == "darwin":
		return os.path.expanduser(r"~/Google Drive/logs/bank.csv")

def get_timestamp(date_str):
	# highcharts count in milliseconds since epoch
	epoch = datetime.datetime.utcfromtimestamp(0)
	delta = timestr_to_datetime(date_str) - epoch
	return delta.total_seconds() * 1000

def timestr_to_datetime(date_str):
	return datetime.datetime.strptime(date_str, "%d/%m/%Y")

def insert_empty_values(res, last_date, date):
	if last_date is None:
		return
	last_date = timestr_to_datetime(last_date).date()
	date = timestr_to_datetime(date).date()
	if date <= last_date:
		return
	last_date += datetime.timedelta(days=1)
	while date > last_date:
		for l in res.values():
			l.append([get_timestamp(last_date.strftime("%d/%m/%Y")), None])
		last_date += datetime.timedelta(days=1)

def csv_enumerator(filename, show_peaks=False):
	with open(filename, "r") as fd:
		titles = fd.readline().strip().split(",")
		for line in fd.readlines():
			if line.startswith("#"):
				if not show_peaks:
					continue
				line = line[1:]
			values = line.strip().split(",")
			yield OrderedDict(zip(titles, values))

def get_json(show_peaks, fake_data, **kwargs):
	filename = get_path()
	if fake_data == "1":
		filename = os.path.join(os.path.dirname(__file__), "fake_bank.csv")
	csv_enum = csv_enumerator(filename, show_peaks == "1")
	what_to_show = [key[len("show_"):] for key, val in kwargs.items()
	                if key.startswith("show_") and val == "1"]
	res = dict([(key, list()) for key in what_to_show])

	last_date = None
	for line in csv_enum:
		date = line.pop("Date")
		insert_empty_values(res, last_date, date)
		last_date = date
		date = get_timestamp(date)
		for key, val in line.items():
			if key in what_to_show:
				val = float(val)
				res[key].append([date, val])
		if "Total" in what_to_show:
			total = sum([float(val) for val in line.values()])
			res["Total"].append([date, total])

	return json.dumps(list(res.items()))

def line_sum(line):
	return sum(float(val) for key, val in line.items() if key != "Date")

def get_titles():
	keys = list(next(csv_enumerator(get_path())).keys())
	keys.append("Total")
	return keys

def get_table(go_back):
	lines = list(csv_enumerator(get_path()))[-2-go_back:]
	prev = lines[0]
	cur = lines[1]
	aaData = []
	for key in get_titles():
		if key == "Date":
			a = cur[key]
			b = prev[key]
			d = ""
		elif key == "Total":
			a = "%.2f" % (line_sum(cur))
			b = "%.2f" % (line_sum(prev))
			d = "%.2f" % (line_sum(cur) - line_sum(prev))
		else:
			a = "%.2f" % (float(cur[key]))
			b = "%.2f" % (float(prev[key]))
			d = "%.2f" % (float(cur[key]) - float(prev[key]))
		aaData.append([key, a, b, d])
	return aaData

class Root(object):
	@cherrypy.expose
	def index(self, **kwargs):
		index_path = os.path.join(os.path.dirname(__file__), "web", "index.html")
		return open(index_path, "r").read()

	@cherrypy.expose
	def table_data(self, go_back, **kwargs):
		aaData = get_table(int(go_back))
		return json.dumps(dict(aaData=aaData))

	@cherrypy.expose
	def jsondata(self, show_peaks, fake_data, **kwargs):
		return get_json(show_peaks, fake_data, **kwargs)

	@cherrypy.expose
	def goback_from_date(self, date):
		date_time = datetime.datetime.fromtimestamp(float(date) / 1000)
		lines = list(csv_enumerator(get_path()))
		go_back_and_dates = [(i, abs(timestr_to_datetime(line["Date"]) - date_time))
		                     for i, line in enumerate(reversed(lines))]
		go_back_and_dates.sort(key=lambda x: x[1])
		return [str(go_back_and_dates[0][0])]

	@cherrypy.expose
	def titles(self):
		return json.dumps(get_titles())

def main():
	current_dir = os.path.dirname(os.path.abspath(__file__))
	conf = {
		"/js":
			{"tools.staticdir.on": True,
			 "tools.staticdir.dir": os.path.join(current_dir, "web")
			},
		"/favicon.ico":
            {"tools.staticfile.on": True,
              "tools.staticfile.filename": os.path.join(current_dir, "web", "favicon.ico")
            }
    }
	cherrypy.config.update({'server.socket_host': IP_ADDR,
		'server.socket_port': PORT,
		'environment': 'production',
		'log.screen': True})
	cherrypy.quickstart(Root(), '/', config=conf)

if __name__ == '__main__':
	main()
