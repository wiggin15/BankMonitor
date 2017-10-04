#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from collections import OrderedDict
# noinspection PyUnresolvedReferences
from assets import *
from assets.common import BankBase, CardBase
from config import get_config_value, get_asset_sections


def get_asset_checker(asset_type):
    class_name = get_config_value(asset_type, "type")
    user = get_config_value(asset_type, "user")
    password = get_config_value(asset_type, "password")
    if not user or not password:
        raise Exception("{} credentials missing".format(asset_type.capitalize()))
    return globals()[class_name](user, password)


def main():
    all_values = OrderedDict()

    bank_total = 0
    card_total = 0
    card_next = 0
    asset_sections = get_asset_sections()
    for asset_section in asset_sections:
        print("{}:".format(asset_section))
        checker = get_asset_checker(asset_section)
        values = checker.get_values()
        values_with_prefix = OrderedDict([("{} - {}".format(asset_section, key), value) for key, value in values.items()])
        all_values.update(values_with_prefix)

        if isinstance(checker, BankBase):
            bank_total += sum(values.values())
        elif isinstance(checker, CardBase):
            card_total += abs(sum(values.values()))
            card_next += checker.get_next()
        else:
            raise Exception("Unknown checker {} of type {}".format(checker, type(checker)))

        print()

    print("Total all banks: {:10,.2f}".format(bank_total))
    print()
    print("All cards: {:,.2f} (next: {:,.2f})".format(card_total, card_next))
    print()
    print("Total: {:10,.2f}".format(bank_total - card_total))
    print()

    return all_values


if __name__ == '__main__':
    main()
    try:
        raw_input()
    except NameError:  # Python 3.x
        input()
