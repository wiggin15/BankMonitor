#!/usr/bin/python
# -*- coding: utf-8 -*-

import ConfigParser

CONFIG_FILE_PATH = "config.ini"

_config = ConfigParser.ConfigParser()
_config.read(CONFIG_FILE_PATH)

def get_config_value(section, option):
	return _config.get(section, option)

def get_config_int(section, option):
	return _config.getint(section, option)

WEBSERVER_IP_ADDR = get_config_value("webserver", "ip")
WEBSERVER_PORT = get_config_int("webserver", "port")
WEBSERVER_FILE_PATH = get_config_value("webserver", "data_file_path")
