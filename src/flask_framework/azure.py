# coding: utf-8
import os
import sys
import logging

from logging.handlers import TimedRotatingFileHandler

import azure.functions as func

from flask_framework.common import BaseApp
from flask_framework.config import Environment
from flask_framework.core import Process
from flask_framework.core.logging import configure_basic_logger, setup_file_logging



def AzureFunctionsApp():
    loglevel = 'warning'
    logging_dir_exist = False
    configure_basic_logger()
    if os.environ.get("LOG_DIR", None):
        setup_file_logging()
    logging.info("Loading configuration file...")
    if "CONFIG_FILE" not in os.environ and not os.path.exists("/etc/flask/"):
        os.environ.setdefault(
            'CONFIG_FILE',
            "config/config.yml" if os.path.exists("config/config.yml")
            else "/etc/flask/config.yml" if os.path.exists("/etc/flask/config.yml")
            else None
        )
    if not 'CONFIG_FILE' in os.environ:
        print('Unable tp detect any configuration files, use CONFIG_FILE env to overide detection')
        exit(255)
    Environment.load(os.environ['CONFIG_FILE'])
    logging.info("Configuration file loaded...")
    try:
        configure_basic_logger(
            'warning' if not 'LEVEL' in Environment.SERVER['LOG'] else Environment.SERVER['LOG']['LEVEL']
        )
    except KeyError as e:
        pass
    try:
        setup_file_logging(
            'warning' if not 'LEVEL' in Environment.SERVER['LOG'] else Environment.SERVER['LOG']['LEVEL']
        )
    except KeyError as e:
        pass
    except FileNotFoundError as e:
        pass
    try:
        loglevel = Environment.SERVER['LOG']['LEVEL']
        logging.getLogger().setLevel(loglevel.upper())
    except KeyError as e:
        pass
    logging_dir_exist = False
    try:
        if not os.path.exists(Environment.SERVER["LOG"]["DIR"]):
            os.mkdir(Environment.SERVER["LOG"]["DIR"], 0o755)
        RotatingLogs = TimedRotatingFileHandler(
            filename=os.path.join(Environment.SERVER["LOG"]["DIR"], 'process.log'),
            when='midnight',
            backupCount=30
        )
        RotatingLogs.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        logging.getLogger().handlers = [
            RotatingLogs
        ]
        logging.info('Logging handler initialized')
        os.environ.setdefault("log_dir", Environment.SERVER["LOG"]["DIR"])
        logging_dir_exist = True
    except KeyError as e:
        pass
    except FileNotFoundError as e:
        pass
    except PermissionError as e:
        pass
    logging.info("Loading options...")
    base_app = BaseApp()
    base_app.load_app()
    return Process.wsgi_setup()
