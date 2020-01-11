from __future__ import print_function

import json
import typing
from abc import ABCMeta, abstractmethod, ABC
from collections import OrderedDict

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


AssetValues = typing.NamedTuple(
    'AssetValues',
    [('values', typing.OrderedDict[str, float]), ('stats', stats.StatsMapping)]
)


class AssetBase(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_values(self):
        # type: () -> AssetValues
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

    def get_values(self):
        # type: () -> AssetValues
        credit_value = self._get_credit()
        card_next = self._get_next()
        return AssetValues(
            OrderedDict([("Credit", credit_value)]),
            stats.StatsMapping([stats.StatCard(credit_value, card_next)])
        )


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

    def get_values(self):
        # type: () -> AssetValues
        exercisable = self._get_exercisable()
        vested = self._get_vested()
        unvested = self._get_unvested()
        return AssetValues(
            OrderedDict([("Exercisable", exercisable)]),
            stats.StatsMapping([stats.StatWorkStock(exercisable, vested, unvested)])
        )


class CommodityBase(AssetBase):
    def __init__(self, asset_section, amount=None, **asset_options):
        if not amount:
            raise Exception("{} amount missing".format(asset_section.capitalize()))
        self._amount = float(amount)

    @abstractmethod
    def _get_value(self):
        # type: () -> float
        raise NotImplementedError()

    def get_values(self):
        # type: () -> AssetValues
        value = self._get_value()
        return AssetValues(
            OrderedDict([("Value", value)]),
            stats.StatsMapping([stats.StatNone(value)])
        )
