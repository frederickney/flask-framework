#!/usr/bin/python3
# coding: utf-8


__author__ = 'Frederick NEY'

import logging
from logging.handlers import TimedRotatingFileHandler

import flask_framework.Server as Server
from flask_framework.Config import Environment
from flask_framework.Database import Database

try:
    import gevent.monkey

    gevent.monkey.patch_all()
except ImportError as e:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s'
    )
    logging.error('{}: gevent not found in python packages'.format(__file__))
    logging.info(
        '{}: gevent is not required if running wsgi as it depends on your worker class you put into the configuration file'
        .format(__file__)
    )
    exit(-1)


def args_parser():
    import argparse
    parser = argparse.ArgumentParser(description='Python FLASK server')
    parser.add_argument(
        '-D', '--debug',
        action='store_true',
        help='Activate debug mode'
    )
    parser.add_argument(
        '-p', '--pid',
        action='store_true',
        help='Create pid file'
    )
    parser.add_argument(
        '-la', '--listening_address',
        help='IP address of the server to listen'
    )
    parser.add_argument(
        '-lp', '--listening_port',
        required=True,
        help='Port of the server to listen'
    )
    args = parser.parse_args()
    return args


def main():
    args = args_parser()
    os.environ.setdefault("log_file", os.environ.get("LOG_FILE", "log/process.log"))
    if not os.path.exists(os.path.dirname(os.environ.get('log_file'))):
        os.mkdir(os.path.dirname(os.environ.get('log_file')), 0o755)
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        filename=os.environ.get('log_file')
    )
    if os.environ.get("LOG_FILE", None) or os.environ.get("LOG_DIR", None):
        os.environ.setdefault("log_dir", os.environ.get("LOG_DIR", "log"))
        os.environ.setdefault(
            "log_file",
            os.environ.get('LOG_FILE', os.path.join(os.environ.get("log_dir"), 'process.log'))
        )
    if os.environ.get("log_file", None):
        logging.basicConfig(
            level=logging.DEBUG if args.debug else logging.INFO,
            format='%(asctime)s %(levelname)s %(message)s',
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
            level=logging.DEBUG if args.debug else logging.INFO,
            format='%(asctime)s %(levelname)s %(message)s'
        )
    logging.info("Starting server...")
    logging.debug("Loading configuration file...")
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
            filename=os.path.join(Environment.SERVER_DATA["LOG"]["DIR"], 'process.log'),
            when='midnight',
            backupCount=30
        )
        RotatingLogs.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        logging.getLogger().handlers = [
            RotatingLogs
        ]
        logging.info('Logging handler initialized')
    except KeyError as e:
        pass
    except FileNotFoundError as e:
        pass
    logging.debug("Configuration file loaded...")
    if 'default' in Environment.Databases:
        logging.debug("Connecting to default database...")
        Database.register_engines(echo=Environment.SERVER_DATA['CAPTURE'])
        Database.init()
        logging.debug("Default database connected...")
    Server.Process.init(tracking_mode=False)
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
    import flask_framework.Extensions as Extensions
    Extensions.load()
    logging.info("Server is now starting...")
    Server.Process.start(args)


if __name__ == '__main__':
    main()
