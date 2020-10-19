#!/usr/bin/python3
# coding: utf-8

__author__ = 'Frederick NEY'

import logging
import os

import Extensions
import Server
from Config import Environment
from Database import Database
from Utils import make_auth, make_controller, make_middleware


def parser():
    import argparse
    parser = argparse.ArgumentParser(description='Python FLASK server')
    parser.add_argument(
        '-cc', '--create-controller',
        help='Create controller',
        required=False
    )
    parser.add_argument(
        '-cm', '--create-middleware',
        help='Create middleware',
        required=False
    )
    args = parser.parse_args()
    if args.create_controller:
        make_controller(os.path.dirname(os.path.realpath(__file__)), args.create_controller)
        exit(0)
    elif args.create_middleware:
        make_middleware(os.path.dirname(os.path.realpath(__file__)), args.create_middleware)
        exit(0)


os.environ.setdefault("log_file", os.environ.get("LOG_FILE", "/var/log/server/process.log"))
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s]: %(message)s',
    filename=os.environ.get('log_file')
)
logging.info("Starting server...")
logging.info("Loading configuration file...")
if 'CONFIG_FILE' in os.environ:
    Environment.load(os.environ['CONFIG_FILE'])
else:
    Environment.load("/etc/server/config.json")
logging.info("Configuration file loaded...")
logging.basicConfig()
logging.getLogger().setLevel(Environment.SERVER_DATA['LOG_LEVEL'].upper()),
logging.debug("Connecting to default database...")
Database.register_engines(Environment.SERVER_DATA['LOG_LEVEL'] == 'debug')
Database.init()
logging.debug("Default database connected...")
Server.Process.init(tracking_mode=False)
# Server.Process.init_sheduler()
logging.debug("Server initialized...")
logging.debug("Loading server routes...")
Server.Process.load_routes()
Server.Process.load_middleware()
Server.Process.load_socket_events()
logging.debug("Server routes loaded...")
# app.teardown_appcontext(Database.save)
logging.info("Server is now starting...")
Extensions.load()
app = Server.Process.instanciate()

if __name__ == '__main__':
    parser()
    app.run()
