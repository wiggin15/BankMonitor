from __future__ import print_function

from abc import ABCMeta, abstractmethod
from enum import Enum


class StatBase(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.__total = 0

    @abstractmethod
    def print_stat(self):
        raise NotImplementedError()

    def add(self, amount):
        self.__total += amount

    def get_total_amount(self):
        return self.__total


class StatNone(StatBase):

    def print_stat(self):
        pass


class StatBank(StatBase):

    def __init__(self):
        super(StatBank, self).__init__()

    def print_stat(self):
        print("All banks: {:,.2f}".format(self.get_total_amount()))


class StatCard(StatBase):

    def __init__(self):
        super(StatCard, self).__init__()
        self.__next = 0

    def add(self, amount, next_amount=0):
        super(StatCard, self).add(amount)
        self.__next += next_amount

    def print_stat(self):
        print("All cards: {:,.2f} (next: {:,.2f})".format(self.get_total_amount(), self.__next))


class StatStockBroker(StatBase):

    def __init__(self):
        super(StatStockBroker, self).__init__()

    def print_stat(self):
        print("All stocks: {:,.2f}".format(self.get_total_amount()))


class StatWorkStock(StatBase):

    def __init__(self):
        super(StatWorkStock, self).__init__()
        self.__vested = 0
        self.__unvested = 0

    def add(self, exercisable, vested=0, unvested=0):
        super(StatWorkStock, self).add(exercisable)
        self.__vested += vested
        self.__unvested += unvested

    def print_stat(self):
        print("All work stocks: {:,.2f} (vested: {:,.2f}, unvested {:,.2f})"
              .format(self.get_total_amount(), self.__vested, self.__unvested))


class StatType(Enum):
    STAT_NONE = (0, StatNone)
    STAT_BANK = (1, StatBank)
    STAT_CARD = (2, StatCard)
    STAT_STOCK_BROKER = (3, StatStockBroker)
    STAT_WORK_STOCK = (4, StatWorkStock)

    def __init__(self, order, stat_class):
        self.order = order
        self.__stat_class = stat_class

    def create_stat_class(self):
        return self.__stat_class()


class StatsDict(dict):

    def __getitem__(self, key):
        if not isinstance(key, StatType):
            raise Exception("Invalid stats type, must be one of the StatType enum values")
        return super(StatsDict, self).setdefault(key, key.create_stat_class())

    def get_all_stats_ordered(self):
        return [x[1] for x in sorted(self.items(), key=lambda pair: pair[0].order)]

    def get_total(self):
        return sum([x.get_total_amount() for x in self.values()])
