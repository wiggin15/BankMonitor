#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from config import get_config_value
from collections import OrderedDict
from assets import BankLeumi, BankOtsar, CardCal, CardLeumi, BankDiscount, BankBeinleumi, CardIsracard


def get_asset_checker(asset_type):
    class_name = get_config_value(asset_type, "type")
    user = get_config_value(asset_type, "user")
    password = get_config_value(asset_type, "password")
    if not user or not password:
        raise Exception("{} credentials missing".format(asset_type.capitalize()))
    return globals()[class_name](user, password)


def main():
    all_values = OrderedDict()

    bank_checker = get_asset_checker("bank")
    bank_values = bank_checker.get_values()
    all_values.update(bank_values)

    card_checker = get_asset_checker("card")
    card_values = card_checker.get_values()
    all_values.update(card_values)

    bank_total = sum(bank_values.values())
    card_total = abs(sum(card_values.values()))
    card_next = card_checker.get_next()

    print()
    print("Total Bank: {:10,.2f}".format(bank_total))
    print()
    print("Card: {:,.2f} (next: {:,.2f})".format(card_total, card_next))
    print()
    print("Total: {:10,.2f}".format(bank_total - card_total))
    print()

    return all_values


if __name__ == '__main__':
    main()
    try:
        raw_input()
    except NameError:        # Python 3.x
        input()
