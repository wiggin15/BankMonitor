from collections import OrderedDict

from assets import stats
from assets.common import AssetBase, print_value


class ConstantValues(AssetBase):
    def __init__(self, asset_section, values=None, **asset_options):
        if not values:
            raise Exception("{} values missing".format(asset_section.capitalize()))
        values_list = values.split(',')
        if len(values_list) % 2 != 0:
            raise Exception("{} values list must contain pairs".format(asset_section.capitalize()))
        self._values_dict = dict(zip(values_list[::2], [float(x) for x in values_list[1::2]]))

    def get_values(self, stats_dict):
        result = OrderedDict([])
        for name, value in self._values_dict.items():
            print_value(value, name)
            stats_dict.get_stat(stats.StatType.STAT_NONE).add(value)
            result[name] = value
        return result
