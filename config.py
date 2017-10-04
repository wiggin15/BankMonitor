#!/usr/bin/python
# -*- coding: utf-8 -*-

try:
    from ConfigParser import ConfigParser
except ImportError:  # Python 3.x
    from configparser import ConfigParser

CONFIG_FILE_PATH = "config.ini"

_config = ConfigParser()
_config.read(CONFIG_FILE_PATH)


def get_config_value(section, option):
    return _config.get(section, option)


def get_config_int(section, option):
    return _config.getint(section, option)


def get_asset_sections():
    all_sections = _config.sections()
    return [x for x in all_sections if x not in {"general", "webserver"}]


WEBSERVER_IP_ADDR = get_config_value("webserver", "ip")
WEBSERVER_PORT = get_config_int("webserver", "port")
CSV_FILE_PATH = get_config_value("general", "data_file_path")
