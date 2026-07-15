#!/usr/bin/python3
# coding: utf-8


__author__ = 'Frederick NEY'

import logging
import os

import flask_framework.core as core
from flask_framework.cli import parser as cli
from flask_framework.common import BaseApp
from flask_framework.config import Environment
from flask_framework.core.logging import configure_basic_logger
from flask_framework.utils import make_controller, make_middleware, make_project


logging.info("Starting server...")
if "CONFIG_FILE" not in os.environ and not os.path.exists("/etc/flask/"):
    os.environ.setdefault(
        'CONFIG_FILE',
        "config/config.yml" if os.path.exists("config/config.yml")
        else "/etc/flask/config.yml" if os.path.exists("/etc/flask/config.yml")
        else None
    )
if not 'CONFIG_FILE' in os.environ:
    print('Unable tp detect any configuration files, use CONFIG_FILE env to override detection')
    exit(255)
logging.info("Loading configuration file...")
Environment.load(os.environ['CONFIG_FILE'])
logging.info("Configuration file loaded...")
try:
    loglevel = Environment.SERVER['LOG']['LEVEL']
    configure_basic_logger(loglevel)
except KeyError as e:
    configure_basic_logger(logging.INFO)
base_app = BaseApp()
base_app.load_app()
logging.info("Server is now starting...")
app = core.Process.get()

if __name__ == '__main__':
    cli()
    app.run(host=Environment.SERVER['BIND']['ADDRESS'], port=Environment.SERVER['BIND']['PORT'])
