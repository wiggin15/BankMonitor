#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function

from collections import OrderedDict

import assets
from assets import stats
from assets.common import all_memoize_caches, AssetBase
from config import get_config_value, get_asset_sections, get_config_options


def get_asset(asset_section):
    # type: (str) -> AssetBase
    class_name = get_config_value(asset_section, "type")
    asset_options = get_config_options(asset_section)
    return getattr(assets, class_name)(asset_section, **asset_options)


def main():
    for cache in all_memoize_caches:
        cache.clear()
    all_values = OrderedDict()
    all_stats = stats.StatsMapping()

    asset_sections = get_asset_sections()
    for asset_section in asset_sections:
        print("{}:".format(asset_section))
        asset = get_asset(asset_section)
        values = asset.get_values()
        values_with_prefix = OrderedDict(
            [("{} - {}".format(asset_section, key), value) for key, value in values.values.items()])
        all_values.update(values_with_prefix)
        all_stats.merge(values.stats)

        print()

    for stat in all_stats.get_all_stats_ordered():
        stat.print_stat()
        print()

    print("Total: {:10,.2f}".format(all_stats.get_total()))
    print()

    return all_values


if __name__ == '__main__':
    main()
    try:
        raw_input()
    except NameError:  # Python 3.x
        input()
