#!/usr/bin/python3
# coding: utf-8

__author__ = 'Frederick NEY'

import logging
import os

import flask_framework.Extensions as Extensions
import flask_framework.Server as Server
from flask_framework.Config import Environment
from flask_framework.Database import Database
from flask_framework.Utils import make_auth, make_controller, make_middleware
from logging.handlers import TimedRotatingFileHandler


def parser():
    import argparse
    parser = argparse.ArgumentParser(description='Python FLASK server')
    parser.add_argument(
        '-cc', '--create-controller',
        help='Create controller',
        required=False
    )
    parser.add_argument(
        '-db', '--database',
        help="Run database operations",
        required=False,
        nargs="+"
    )
    parser.add_argument(
        '-s', '--shell',
        help="Run interactive shell",
        required=False,
        action="store_true"
    )
    parser.add_argument(
        '-r', '--run',
        help="Run server",
        required=False,
        action="store_true"
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
    elif args.database or args.shell or args.run:
        import sys
        for i in range(0, len(sys.argv)):
            if sys.argv[i] == '-db' or sys.argv[i] == '--database':
                sys.argv[i] = 'database'
            elif sys.argv[i] == '-s' or sys.argv[i] == '--shell':
                sys.argv[i] = 'shell'
            elif sys.argv[i] == '-r' or sys.argv[i] == '--run':
                sys.argv[i] = 'runserver'
        from Database.migration import Migrate
        Migrate.run(app)
        exit(0)



if os.environ.get("LOG_FILE", None) or os.environ.get("LOG_DIR", None):
    os.environ.setdefault("log_dir", os.environ.get("LOG_DIR", "/var/log/server/"))
    os.environ.setdefault("log_file", os.environ.get('LOG_FILE', os.path.join(os.environ.get("log_dir"), 'process.log')))
if os.environ.get("log_file", None):
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s]: %(message)s',
        handlers=[
            TimedRotatingFileHandler(
                filename=os.environ.get('log_file'),
                when='midnight',
                backupCount=30
            )
        ]
    )
else:
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s]: %(message)s'
    )
logging.info("Starting server...")
logging.info("Loading configuration file...")
if 'CONFIG_FILE' in os.environ:
    Environment.load(os.environ['CONFIG_FILE'])
else:
    Environment.load("/etc/server/config.json")
try:
    loglevel = Environment.SERVER_DATA['LOG']['LEVEL']
    logging.getLogger().setLevel(loglevel.upper())
except KeyError as e:
    pass
try:
    RotatingLogs = TimedRotatingFileHandler(
        filename=os.path.join(Environment.SERVER_DATA["LOG"]['DIR'], 'process.log'),
        when='midnight',
        backupCount=30
    )
    RotatingLogs.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s]: %(message)s'))
    logging.getLogger().handlers = [
        RotatingLogs
    ]
    logging.info('Logging handler initialized')
except KeyError as e:
    pass
except FileNotFoundError as e:
    pass
logging.info("Configuration file loaded...")
logging.debug("Connecting to default database...")
Database.register_engines(Environment.SERVER_DATA['LOG']['LEVEL'] == 'debug')
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
app = Server.Process.init()

if __name__ == '__main__':
    parser()
    app.run(host=Environment.SERVER_DATA['BIND']['ADDRESS'], port=Environment.SERVER_DATA['BIND']['PORT'])
