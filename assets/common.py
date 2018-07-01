from __future__ import print_function

import json
from abc import ABCMeta, abstractmethod
from collections import OrderedDict

import requests

from assets import stats

HEADERS_USER_AGENT = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100"
}


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
    api_result = requests.get("https://free.currencyconverterapi.com/api/v5/convert?q=USD_ILS&compact=ultra").text
    api_data = json.loads(api_result)
    return api_data["USD_ILS"]


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

    @abstractmethod
    def get_values(self, stats_dict):
        raise NotImplementedError()


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
    pass


class CardBase(AuthenticatedAssetBase):
    @abstractmethod
    def _get_credit(self):
        raise NotImplementedError()

    @abstractmethod
    def _get_next(self):
        raise NotImplementedError()

    def get_values(self, stats_dict):
        credit_value = self._get_credit()
        card_next = self._get_next()
        stats_dict.get_stat(stats.StatType.STAT_CARD).add(credit_value, card_next)
        return OrderedDict([("Credit", credit_value)])


class WorkStockBase(AuthenticatedAssetBase):
    @abstractmethod
    def _get_exercisable(self):
        raise NotImplementedError()

    @abstractmethod
    def _get_vested(self):
        raise NotImplementedError()

    @abstractmethod
    def _get_unvested(self):
        raise NotImplementedError()

    def get_values(self, stats_dict):
        exercisable = self._get_exercisable()
        vested = self._get_vested()
        unvested = self._get_unvested()
        stats_dict.get_stat(stats.StatType.STAT_WORK_STOCK).add(exercisable, vested, unvested)
        return OrderedDict([("Exercisable", exercisable)])


class CommodityBase(AssetBase):
    def __init__(self, asset_section, amount=None, **asset_options):
        if not amount:
            raise Exception("{} amount missing".format(asset_section.capitalize()))
        self._amount = float(amount)

    @abstractmethod
    def _get_value(self):
        raise NotImplementedError()

    def get_values(self, stats_dict):
        value = self._get_value()
        stats_dict.get_stat(stats.StatType.STAT_NONE).add(value)
        return OrderedDict([("Value", value)])
