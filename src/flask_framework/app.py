#!/usr/bin/python3
# coding: utf-8


__author__ = 'Frederick NEY'

import logging
import os

import flask_framework.Extensions as Extensions
import flask_framework.Server as Server
from flask_framework.Config import Environment
from flask_framework.Database import Database
from flask_framework.Utils import make_controller, make_middleware, make_project


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
    parser.add_argument(
        '-db', '--database',
        help="Run database operations see Flask-Migrate for usages",
        required=False,
        nargs="+"
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
    elif args.database:
        from flask_framework.Database.migration import Migrate
        Migrate.run(app, args.database)
        exit(0)


logging.info("Starting server...")
logging.info("Loading configuration file...")
Environment.load(os.environ.get('CONFIG_FILE', "/etc/server/config.json"))
try:
    loglevel = Environment.SERVER_DATA['LOG']['LEVEL']
    logging.basicConfig(
        level=loglevel.upper(),
        format='%(asctime)s %(levelname)s %(message)s'
    )
except KeyError as e:
    logging.basicConfig(
        level=logging.getLevelName(logging.INFO),
        format='%(asctime)s %(levelname)s %(message)s'
    )
logging.debug("Connecting to default database...")
Database.register_engines(echo=Environment.SERVER_DATA['CAPTURE'])
Database.init()
logging.debug("Default database connected...")
Server.Process.init(tracking_mode=False)
# Server.Process.init_sheduler()
logging.debug("Server initialized...")
Server.Process.load_plugins()
logging.debug("Loading server routes...")
Server.Process.load_routes()
Server.Process.load_middleware()
logging.debug("Server routes loaded...")
logging.debug("Loading websocket events")
Server.Process.load_socket_events()
logging.debug("Websocket events loaded...")
# app.teardown_appcontext(Database.save)
Extensions.load()
logging.info("Server is now starting...")
app = Server.Process.get()

if __name__ == '__main__':
    parser()
    app.run(host=Environment.SERVER_DATA['BIND']['ADDRESS'], port=Environment.SERVER_DATA['BIND']['PORT'])
