from __future__ import print_function

def format_value(value_text, print_name=None):
    val = float(value_text.replace(",", ""))
    if print_name is not None:
        print("{}: {:10,.2f}".format(print_name, val))
    return val

class AssetBase(object):
    def __init__(self, username, password):
        self._username = username
        self._password = password
        self._session = self._establish_session(username, password)

    def _establish_session(self, username, password):
        raise NotImplementedError()

    def get_values(self):
        raise NotImplementedError()
