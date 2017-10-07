#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from collections import OrderedDict
# noinspection PyUnresolvedReferences
from assets import *
from assets.common import BankBase, CardBase, StockBrokerBase
from config import get_config_value, get_asset_sections, get_config_options


def get_asset_checker(asset_section):
    class_name = get_config_value(asset_section, "type")
    asset_options = get_config_options(asset_section)
    return globals()[class_name](asset_section, **asset_options)


def main():
    all_values = OrderedDict()

    bank_total = 0
    card_total = 0
    card_next = 0
    stock_exercisable = 0
    stock_vested = 0
    stock_unvested = 0
    asset_sections = get_asset_sections()
    for asset_section in asset_sections:
        print("{}:".format(asset_section))
        checker = get_asset_checker(asset_section)

        if isinstance(checker, BankBase):
            values = checker.get_values()
            bank_total += sum(values.values())
        elif isinstance(checker, CardBase):
            credit_value = checker.get_credit()
            values = OrderedDict([("Credit", credit_value)])
            card_total += abs(credit_value)
            card_next += checker.get_next()
        elif isinstance(checker, StockBrokerBase):
            exercisable_value = checker.get_exercisable()
            values = OrderedDict([("Exercisable", exercisable_value)])
            stock_exercisable += exercisable_value
            stock_vested += checker.get_vested()
            stock_unvested += checker.get_unvested()
        else:
            raise Exception("Unknown checker {} of type {}".format(checker, type(checker)))

        values_with_prefix = OrderedDict(
            [("{} - {}".format(asset_section, key), value) for key, value in values.items()])
        all_values.update(values_with_prefix)

        print()

    print("Total all banks: {:10,.2f}".format(bank_total))
    print()
    print("All cards: {:,.2f} (next: {:,.2f})".format(card_total, card_next))
    print()
    print("All stock brokers: {:,.2f} (vested: {:,.2f}, unvested {:,.2f})"
          .format(stock_exercisable, stock_vested, stock_unvested))
    print()
    print("Total: {:10,.2f}".format(bank_total - card_total + stock_exercisable))
    print()

    return all_values


if __name__ == '__main__':
    main()
    try:
        raw_input()
    except NameError:  # Python 3.x
        input()
