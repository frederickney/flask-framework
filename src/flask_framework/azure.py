# coding: utf-8

import logging

from flask_framework.Config import Environment
from flask_framework.Database import Database
from flask_framework.Server import Process


def AzureFunctionsApp():
    import os
    from logging.handlers import TimedRotatingFileHandler
    loglevel = 'warning'
    logging_dir_exist = False
    if os.environ.get("LOG_DIR", None):
        os.environ.setdefault("log_dir", os.environ.get("LOG_DIR", "/var/log/server/"))
        os.environ.setdefault("log_file", os.path.join(os.environ.get("log_dir"), 'process.log'))
        if not os.path.exists(os.path.dirname(os.environ.get('log_file'))):
            os.mkdir(os.path.dirname(os.environ.get('log_file')), 0o755)
    if os.environ.get("log_file", None):
        logging.basicConfig(
            level=loglevel.upper(),
            format='%(asctime)s %(levelname)s %(message)s',
            handlers=[
                TimedRotatingFileHandler(
                    filename=os.environ.get('log_file'),
                    when='midnight',
                    backupCount=30
                )
            ]
        )
        logging_dir_exist = True
    else:
        logging.basicConfig(
            level=loglevel.upper(),
            format='%(asctime)s %(levelname)s %(message)s',
        )
    logging.info("Loading configuration file...")
    if 'CONFIG_FILE' in os.environ:
        Environment.load(os.environ['CONFIG_FILE'])
    else:
        Environment.load("/etc/server/config.json")
        os.environ.setdefault('CONFIG_FILE', "/etc/server/config.json")
    logging.info("Configuration file loaded...")
    try:
        loglevel = Environment.SERVER_DATA['LOG']['LEVEL']
        logging.getLogger().setLevel(loglevel.upper())
    except KeyError as e:
        pass
    logging_dir_exist = False
    try:
        if not os.path.exists(Environment.SERVER_DATA["LOG"]["DIR"]):
            os.mkdir(Environment.SERVER_DATA["LOG"]["DIR"], 0o755)
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
        os.environ.setdefault("log_dir", Environment.SERVER_DATA["LOG"]["DIR"])
        logging_dir_exist = True
    except KeyError as e:
        pass
    except FileNotFoundError as e:
        pass
    except PermissionError as e:
        pass
    logging.info("Loading options...")
    if len(Environment.Databases) > 0:
        logging.debug("Connecting to database(s)...")
        Database.register_engines(echo=Environment.SERVER_DATA['CAPTURE'])
        Database.init()
        logging.debug("Database(s) connected...")
    logging.info("Initializing the server...")
    Process.init(tracking_mode=False)
    logging.info("Server initialized...")
    Process.load_plugins()
    logging.debug("Loading server routes...")
    Process.load_routes()
    Process.load_middleware()
    logging.debug("Server routes loaded...")
    logging.debug("Loading websocket events")
    Process.load_socket_events()
    logging.debug("Websocket events loaded...")
    logging.info("Options loaded...")
    logging.info("Starting the server...")
    return Process.wsgi_setup()
