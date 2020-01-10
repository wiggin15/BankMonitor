from __future__ import print_function

import json
from abc import ABCMeta, abstractmethod, ABC
from collections import OrderedDict
from typing import cast

import requests

from . import stats

HEADERS_USER_AGENT = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"
}


def print_value(val, print_name):
    # type: (float, str) -> None
    print("{}: {:10,.2f}".format(print_name, val))


def format_value(value_text, print_name=None):
    # type: (str, str) -> float
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
    # type: () -> float
    api_result = requests.get(
        "https://free.currencyconverterapi.com/api/v5/convert?q=USD_ILS&compact=ultra&apiKey=207f0d8f1a97997f891a").text
    api_data = json.loads(api_result)
    return api_data["USD_ILS"]


def convert_usd_to_ils(usd_value):
    # type: (float) -> float
    ratio = get_usd_to_ils_conversion_ratio()
    return usd_value * ratio


@memoize
def get_stock_value(stock_name):
    # type: (str) -> float
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
        # type: (stats.StatsDict) -> OrderedDict[str, float]
        raise NotImplementedError()


class AuthenticatedAssetBase(AssetBase):
    def __init__(self, asset_section, user=None, password=None, **asset_options):
        # type: (str, str, str, ...) -> None
        self._username = user
        self._password = password
        if not self._username or not self._password:
            raise Exception("{} credentials missing".format(asset_section.capitalize()))

        self._session = self._establish_session(self._username, self._password)

    @abstractmethod
    def _establish_session(self, username, password):
        # type: (str, str) -> requests.Session
        raise NotImplementedError()


class BankBase(AuthenticatedAssetBase, ABC):
    pass


class CardBase(AuthenticatedAssetBase):
    @abstractmethod
    def _get_credit(self):
        # type: () -> float
        raise NotImplementedError()

    @abstractmethod
    def _get_next(self):
        # type: () -> float
        raise NotImplementedError()

    def get_values(self, stats_dict):
        # type: (stats.StatsDict) -> OrderedDict[str, float]
        credit_value = self._get_credit()
        card_next = self._get_next()
        cast(stats.StatCard, stats_dict[stats.StatType.STAT_CARD]).add(credit_value, card_next)
        return OrderedDict([("Credit", credit_value)])


class WorkStockBase(AuthenticatedAssetBase):
    @abstractmethod
    def _get_exercisable(self):
        # type: () -> float
        raise NotImplementedError()

    @abstractmethod
    def _get_vested(self):
        # type: () -> float
        raise NotImplementedError()

    @abstractmethod
    def _get_unvested(self):
        # type: () -> float
        raise NotImplementedError()

    def get_values(self, stats_dict):
        # type: (stats.StatsDict) -> OrderedDict[str, float]
        exercisable = self._get_exercisable()
        vested = self._get_vested()
        unvested = self._get_unvested()
        cast(stats.StatWorkStock, stats_dict[stats.StatType.STAT_WORK_STOCK]).add(exercisable, vested, unvested)
        return OrderedDict([("Exercisable", exercisable)])


class CommodityBase(AssetBase):
    def __init__(self, asset_section, amount=None, **asset_options):
        if not amount:
            raise Exception("{} amount missing".format(asset_section.capitalize()))
        self._amount = float(amount)

    @abstractmethod
    def _get_value(self):
        # type: () -> float
        raise NotImplementedError()

    def get_values(self, stats_dict):
        # type: (stats.StatsDict) -> OrderedDict[str, float]
        value = self._get_value()
        stats_dict[stats.StatType.STAT_NONE].add(value)
        return OrderedDict([("Value", value)])
