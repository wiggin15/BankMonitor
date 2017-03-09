#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request
import json
import datetime
from collections import OrderedDict
from config import WEBSERVER_IP_ADDR, WEBSERVER_PORT, CSV_FILE_PATH, get_config_value

app = Flask(__name__, template_folder="web", static_folder="web")


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


def csv_enumerator(show_peaks=False):
    with open(CSV_FILE_PATH, "r") as fd:
        titles = fd.readline().strip().split(",")
        for line in fd.readlines():
            if line.startswith("#"):
                if not show_peaks:
                    continue
                line = line[1:]
            values = line.strip().split(",")
            yield OrderedDict(zip(titles, values))


def get_max_json():
    per_month = dict()
    for k in csv_enumerator():
        d = k.pop("Date").split('/', 1)[-1]
        v = sum([float(x) for x in k.values()])
        per_month.setdefault(d, list()).append(v)
    per_month_max = [(k, max(v)) for k, v in per_month.items()]
    per_month_max.sort(key=lambda k: [int(x) for x in k[0].split("/")[::-1]])
    return dict(Total=per_month_max)


@app.route("/jsondata")
def get_json():
    show_peaks = request.args.get('show_peaks')
    per_month_max = request.args.get('per_month_max')
    if per_month_max == "1":
        return json.dumps(list(get_max_json().items()))
    csv_enum = csv_enumerator(show_peaks == "1")
    hide = get_config_value("webserver", "hide").strip().split(",")
    res = OrderedDict()

    last_date = None
    for line in csv_enum:
        date = line.pop("Date")
        insert_empty_values(res, last_date, date)
        last_date = date
        date = get_timestamp(date)
        for key, val in line.items():
            if key not in hide:
                val = float(val)
                res.setdefault(key, list()).append([date, val])
        total = sum([float(val) for val in line.values()])
        res.setdefault("Total", list()).append([date, total])

    return json.dumps(list(res.items()))


@app.route("/")
def index():
    return render_template("index.html")


def test_read():
    """ dry read to make sure csv file exists and has at least one line of data """
    try:
        next(csv_enumerator())
    except StopIteration:
        print("ERROR: No data in CSV file")
        return False
    except IOError:
        print("ERROR: CSV file not found")
        return False
    return True


def main():
    if test_read():
        app.run(host=WEBSERVER_IP_ADDR, port=WEBSERVER_PORT, debug=True, use_reloader=False)


if __name__ == '__main__':
    main()
