from __future__ import print_function

from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import List, Iterable


class StatType(Enum):
    STAT_NONE = 0
    STAT_BANK = 1
    STAT_CARD = 2
    STAT_STOCK_BROKER = 3
    STAT_WORK_STOCK = 4

    def __init__(self, order):
        # type: (int) -> None
        self.order = order


class StatBase(object):
    __metaclass__ = ABCMeta

    def __init__(self, stat_type, total=0):
        # type: (StatType, float) -> None
        self._total = total
        self.__stat_type = stat_type

    def add(self, amount):
        # type: (float) -> None
        self._total += amount

    def merge(self, other):
        # type: (StatBase) -> None
        assert isinstance(other, StatBase)
        self.add(other.get_total_amount())

    @abstractmethod
    def print_stat(self):
        # type: () -> None
        raise NotImplementedError()

    def get_total_amount(self):
        # type: () -> float
        return self._total

    def get_stat_type(self):
        # type: () -> StatType
        return self.__stat_type


class StatNone(StatBase):

    def __init__(self, total=0):
        # type: (float) -> None
        super(StatNone, self).__init__(StatType.STAT_NONE, total)

    def print_stat(self):
        # type: () -> None
        pass


class StatBank(StatBase):

    def __init__(self, total=0):
        # type: (float) -> None
        super(StatBank, self).__init__(StatType.STAT_BANK, total)

    def print_stat(self):
        # type: () -> None
        print("All banks: {:,.2f}".format(self.get_total_amount()))


class StatCard(StatBase):

    def __init__(self, amount=0, next_amount=0):
        # type: (float, float) -> None
        super(StatCard, self).__init__(StatType.STAT_CARD, amount)
        self.__next_amount = next_amount

    def add(self, amount, next_amount=0):
        # type: (float, float) -> None
        super(StatCard, self).add(amount)
        self.__next_amount += next_amount

    def merge(self, other):
        # type: (StatCard) -> None
        assert isinstance(other, StatCard)
        self.add(other._total, other.__next_amount)

    def print_stat(self):
        # type: () -> None
        print("All cards: {:,.2f} (next: {:,.2f})".format(self.get_total_amount(), self.__next_amount))


class StatStockBroker(StatBase):

    def __init__(self, total=0):
        # type: (float) -> None
        super(StatStockBroker, self).__init__(StatType.STAT_STOCK_BROKER, total)

    def print_stat(self):
        # type: () -> None
        print("All stocks: {:,.2f}".format(self.get_total_amount()))


class StatWorkStock(StatBase):

    def __init__(self, total=0, vested=0, unvested=0):
        # type: (float, float, float) -> None
        super(StatWorkStock, self).__init__(StatType.STAT_WORK_STOCK, total)
        self.__vested = vested
        self.__unvested = unvested

    def add(self, exercisable, vested=0, unvested=0):
        # type: (float, float, float) -> None
        super(StatWorkStock, self).add(exercisable)
        self.__vested += vested
        self.__unvested += unvested

    def merge(self, other):
        # type: (StatWorkStock) -> None
        assert isinstance(other, StatWorkStock)
        self.add(other._total, other.__vested, other.__unvested)

    def print_stat(self):
        # type: () -> None
        print("All work stocks: {:,.2f} (vested: {:,.2f}, unvested {:,.2f})"
              .format(self.get_total_amount(), self.__vested, self.__unvested))


class StatsMapping(object):

    def __init__(self, stats=None):
        # type: (Iterable[StatBase]) -> None
        self.__mapping = dict()
        if stats:
            for x in stats:
                self.__mapping[x.get_stat_type()] = x

    def merge(self, other):
        # type: (StatsMapping) -> None
        for k, v in other.__mapping.items():
            cur_value = self.__mapping.get(k)
            if cur_value:
                cur_value.merge(v)
            else:
                self.__mapping[k] = v

    def get_all_stats_ordered(self):
        # type: () -> List[StatBase]
        return [x[1] for x in sorted(self.__mapping.items(), key=lambda pair: pair[0].order)]

    def get_total(self):
        # type: () -> float
        return sum([x.get_total_amount() for x in self.__mapping.values()])
