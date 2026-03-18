#!/usr/bin/python3
# coding: utf-8


__author__ = 'Frederick NEY'

import logging
import os

import flask_framework.core as core
from flask_framework.common import BaseApp
from flask_framework.config import Environment
from flask_framework.core.logging import configure_basic_logger
from flask_framework.utils import make_controller, make_middleware, make_project


def parser():
    import argparse
    parser = argparse.ArgumentParser(description='Python FLASK server')
    parser.add_argument(
        '-cp', '--create-project',
        help='Create project\nexample:\npython -m flask_framework.cli --create-project webapp',
        required=False
    )
    parser.add_argument(
        '-cc', '--create-controller',
        help='Create controller\nexample:\npython -m flask_framework.cli --create-controller controllers/web/login',
        required=False
    )
    parser.add_argument(
        '-cm', '--create-middleware',
        help='Create middleware\nexample:\npython -m flask_framework.cli --create-middleware test',
        required=False
    )
    args = parser.parse_args()
    if args.create_project:
        make_project(os.getcwd(), args.create_project, os.path.dirname(os.path.realpath(__file__)))
        exit(0)
    elif args.create_controller:
        make_controller(os.getcwd(), args.create_controller)
        exit(0)
    elif args.create_middleware:
        make_middleware(os.getcwd(), args.create_middleware)
        exit(0)


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
core.Process.init(tracking_mode=False)
logging.info("Server is now starting...")
app = core.Process.get()

if __name__ == '__main__':
    parser()
    app.run(host=Environment.SERVER['BIND']['ADDRESS'], port=Environment.SERVER['BIND']['PORT'])
