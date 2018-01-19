from __future__ import print_function

import json
from abc import ABCMeta, abstractmethod

import requests


def print_value(val, print_name):
    print("{}: {:10,.2f}".format(print_name, val))


def format_value(value_text, print_name=None):
    val = float(value_text.replace(",", ""))
    if print_name is not None:
        print_value(val, print_name)
    return val


all_memoize_caches = []


def memoize(func):
    memo = {}
    all_memoize_caches.append(memo)

    def wrapper(*args):
        if args in memo:
            return memo[args]
        else:
            rv = func(*args)
            memo[args] = rv
            return rv

    return wrapper


@memoize
def get_usd_to_ils_conversion_ratio():
    api_result = requests.get("https://api.fixer.io/latest?base=USD&symbols=ILS").text
    api_data = json.loads(api_result)
    return api_data["rates"]["ILS"]


def convert_usd_to_ils(usd_value):
    ratio = get_usd_to_ils_conversion_ratio()
    return usd_value * ratio


@memoize
def get_stock_value(stock_name):
    url = "https://www.alphavantage.co/query?apikey=97DT8FPVN9WQQGIQ&function=TIME_SERIES_DAILY&symbol={}" \
        .format(stock_name)
    api_result = requests.get(url).text
    api_data = json.loads(api_result)
    daily_stats = api_data["Time Series (Daily)"]
    return float(daily_stats[max(daily_stats.keys())]["1. open"])


class AssetBase(object):
    __metaclass__ = ABCMeta


class AuthenticatedAssetBase(AssetBase):
    def __init__(self, asset_section, user=None, password=None, **asset_options):
        self._username = user
        self._password = password
        if not self._username or not self._password:
            raise Exception("{} credentials missing".format(asset_section.capitalize()))

        self._session = self._establish_session(self._username, self._password)

    @abstractmethod
    def _establish_session(self, username, password):
        raise NotImplementedError()


class BankBase(AuthenticatedAssetBase):
    @abstractmethod
    def get_values(self):
        raise NotImplementedError()


class CardBase(AuthenticatedAssetBase):
    @abstractmethod
    def get_credit(self):
        raise NotImplementedError()

    @abstractmethod
    def get_next(self):
        raise NotImplementedError()


class StockBrokerBase(AuthenticatedAssetBase):
    @abstractmethod
    def get_exercisable(self):
        raise NotImplementedError()

    @abstractmethod
    def get_vested(self):
        raise NotImplementedError()

    @abstractmethod
    def get_unvested(self):
        raise NotImplementedError()


class CommodityBase(AssetBase):
    def __init__(self, asset_section, amount=None, **asset_options):
        if not amount:
            raise Exception("{} amount missing".format(asset_section.capitalize()))
        self._amount = float(amount)

    @abstractmethod
    def get_value(self):
        raise NotImplementedError()
