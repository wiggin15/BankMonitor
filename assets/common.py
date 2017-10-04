from __future__ import print_function
from abc import ABCMeta, abstractmethod


def format_value(value_text, print_name=None):
    val = float(value_text.replace(",", ""))
    if print_name is not None:
        print("{}: {:10,.2f}".format(print_name, val))
    return val


class AssetBase(object):
    __metaclass__ = ABCMeta

    def __init__(self, username, password):
        self._username = username
        self._password = password
        self._session = self._establish_session(username, password)

    @abstractmethod
    def _establish_session(self, username, password):
        raise NotImplementedError()

    @abstractmethod
    def get_values(self):
        raise NotImplementedError()


# noinspection PyAbstractClass
class BankBase(AssetBase):
    pass


class CardBase(AssetBase):
    @abstractmethod
    def get_next(self):
        raise NotImplementedError()
