#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
import time
import os
import bank
from config import CSV_FILE_PATH
from collections import OrderedDict


def update():
    date = time.strftime("%d/%m/%Y")
    values = OrderedDict([("Date", date)])
    values.update(bank.main())

    new_content = ','.join([str(x) for x in values.values()]) + "\r\n"
    if not os.path.isfile(CSV_FILE_PATH):
        new_content = ','.join(values.keys()) + "\r\n" + new_content
    new_content = new_content.encode("ascii")
    with open(CSV_FILE_PATH, "ab+") as f:
        f.write(new_content)


if __name__ == '__main__':
    update()
