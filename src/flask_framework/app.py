#!/usr/bin/python3
# coding: utf-8


__author__ = 'Frederick NEY'

import logging
import os

import flask_framework.extensions as extensions
from flask_framework.config import Environment
from flask_framework.core import Process
from flask_framework.database import Database
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
logging.info("Loading configuration file...")
Environment.load(os.environ.get('CONFIG_FILE', "/etc/server/config.json"))
try:
    loglevel = Environment.SERVER['LOG']['LEVEL']
    logging.basicConfig(
        level=loglevel.upper(),
        format='%(asctime)s %(levelname)s %(message)s'
    )
except KeyError as e:
    logging.basicConfig(
        level=logging.getLevelName(logging.INFO),
        format='%(asctime)s %(levelname)s %(message)s'
    )
logging.debug("Connecting to database(s)...")
Database.register_engines(echo=Environment.SERVER['CAPTURE'])
Database.init()
logging.debug("Database(s) connected...")
Process.init(tracking_mode=False)
# Server.Process.init_sheduler()
logging.debug("Server initialized...")
Process.load_plugins()
logging.debug("Loading server routes...")
Process.load_routes()
Process.load_middleware()
logging.debug("Server routes loaded...")
logging.debug("Loading websocket events")
Process.load_socket_events()
logging.debug("Websocket events loaded...")
# app.teardown_appcontext(Database.save)
extensions.load()
logging.info("Server is now starting...")
app = Process.get()

if __name__ == '__main__':
    parser()
    app.run(host=Environment.SERVER['BIND']['ADDRESS'], port=Environment.SERVER['BIND']['PORT'])
