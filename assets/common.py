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


def get_usd_to_ils_conversion_ratio():
    api_result = requests.get("https://api.fixer.io/latest?base=USD&symbols=ILS").text
    api_data = json.loads(api_result)
    return api_data["rates"]["ILS"]


def convert_usd_to_ils(usd_value):
    try:
        ratio = convert_usd_to_ils.conversion_ratio
    except AttributeError:
        convert_usd_to_ils.conversion_ratio = get_usd_to_ils_conversion_ratio()
        ratio = convert_usd_to_ils.conversion_ratio

    return usd_value * ratio


class AssetBase(object):
    __metaclass__ = ABCMeta

    def __init__(self, asset_section, asset_options):
        self._username = asset_options.get("user", None)
        self._password = asset_options.get("password", None)
        if not self._username or not self._password:
            raise Exception("{} credentials missing".format(asset_section.capitalize()))

        self._session = self._establish_session(self._username, self._password)

    @abstractmethod
    def _establish_session(self, username, password):
        raise NotImplementedError()


class BankBase(AssetBase):
    @abstractmethod
    def get_values(self):
        raise NotImplementedError()


class CardBase(AssetBase):
    @abstractmethod
    def get_credit(self):
        raise NotImplementedError()

    @abstractmethod
    def get_next(self):
        raise NotImplementedError()


class StockBrokerBase(AssetBase):
    def __init__(self, asset_section, asset_options):
        super(StockBrokerBase, self).__init__(asset_section, asset_options)
        self._tax_percentage = float(asset_options.get("tax_percentage", 0))

    @abstractmethod
    def get_exercisable(self):
        raise NotImplementedError()

    @abstractmethod
    def get_vested(self):
        raise NotImplementedError()

    @abstractmethod
    def get_unvested(self):
        raise NotImplementedError()
