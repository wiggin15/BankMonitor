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
    what_to_show = [key[len("show_"):] for key, val in request.args.items()
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
    keys = list(next(csv_enumerator()).keys())
    hide = get_config_value("webserver", "hide").strip()
    if hide:
        [keys.remove(asset) for asset in hide.split(",")]
    keys.append("Total")
    return keys


@app.route("/table_data")
def get_table():
    go_back = int(request.args.get('go_back'))
    lines = list(csv_enumerator())[-2-go_back:]
    prev = lines[0]
    cur = lines[1] if len(lines) > 1 else lines[0]
    data = []
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
        data.append([key, a, b, d])
    return json.dumps(dict(data=data))


@app.route("/goback_from_date")
def goback_from_date():
    date = request.args.get('date')
    date_time = datetime.datetime.fromtimestamp(float(date) / 1000)
    lines = list(csv_enumerator())
    go_back_and_dates = [(i, abs(timestr_to_datetime(line["Date"]) - date_time))
                         for i, line in enumerate(reversed(lines))]
    go_back_and_dates.sort(key=lambda x: x[1])
    return str(go_back_and_dates[0][0])


@app.route('/titles')
def titles():
    return json.dumps(get_titles())


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
