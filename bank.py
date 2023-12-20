from __future__ import print_function
from collections import OrderedDict
from assets.common import BankBase, CardBase, StockBrokerBase, all_memoize_caches
from config import get_config_value, get_asset_sections, get_config_options
import assets


def get_asset(asset_section):
    class_name = get_config_value(asset_section, "type")
    asset_options = get_config_options(asset_section)
    return getattr(assets, class_name)(asset_section, **asset_options)


def main():
    for cache in all_memoize_caches:
        cache.clear()
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
        asset = get_asset(asset_section)

        if isinstance(asset, BankBase):
            values = asset.get_values()
            bank_total += sum(values.values())
        elif isinstance(asset, CardBase):
            credit_value = asset.get_credit()
            values = OrderedDict([("Credit", credit_value)])
            card_total += abs(credit_value)
            card_next += asset.get_next()
        elif isinstance(asset, StockBrokerBase):
            exercisable_value = asset.get_exercisable()
            values = OrderedDict([("Exercisable", exercisable_value)])
            stock_exercisable += exercisable_value
            stock_vested += asset.get_vested()
            stock_unvested += asset.get_unvested()
        else:
            raise Exception("Unknown asset {} of type {}".format(asset, type(asset)))

        values_with_prefix = OrderedDict(
            [("{} - {}".format(asset_section, key), value) for key, value in values.items()])
        all_values.update(values_with_prefix)

        print()

    print("Total all banks: {:10,.2f}".format(bank_total))
    print()
    print("All cards: {:,.2f} (next: {:,.2f})".format(card_total, card_next))
    print()
    if stock_exercisable != 0 or stock_vested != 0 or stock_unvested != 0:
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
