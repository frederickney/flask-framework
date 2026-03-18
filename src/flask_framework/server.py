#!/usr/bin/python3
# coding: utf-8


__author__ = 'Frederick NEY'

import logging
import os
import sys

from flask_framework.common import BaseApp
from flask_framework.config import Environment
from flask_framework.core import Process
from flask_framework.core.logging import configure_basic_logger, setup_file_logging


try:
    import gevent.monkey

    gevent.monkey.patch_all()
except ImportError as e:
    configure_basic_logger('info')
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
    parser.add_argument(
        '-d', '--disable-log-files',
        action='store_true',
        required=False,
        help='Deactivate logs to file'
    )

    args = parser.parse_args()
    return args


def main():
    """
        main entry point for flask_framework.server
        """
    if os.getcwd() not in sys.path:
        sys.path.append(os.getcwd())
    args = args_parser()
    configure_basic_logger(None)
    if not args.disable_log_files:
        setup_file_logging()
    if os.environ.get("LOG_DIR", None):
        os.environ.setdefault("log_dir", os.environ.get("LOG_DIR", "/var/log/flask"))
    if not args.disable_log_files:
        os.environ.setdefault("log_file", os.environ.get("LOG_FILE", "log/process.log"))
        if not os.path.exists(os.path.dirname(os.environ.get('log_file'))):
            os.mkdir(os.path.dirname(os.environ.get('log_file')), 0o755)
        setup_file_logging()
    logging.info("Starting server...")
    logging.debug("Loading configuration file...")
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
    try:
        configure_basic_logger(
            'warning' if not 'LEVEL' in Environment.SERVER['LOG'] else Environment.SERVER['LOG']['LEVEL']
        )
    except KeyError as e:
        pass
    try:
        if not args.disable_log_files:
            setup_file_logging(
                'warning' if not 'LEVEL' in Environment.SERVER['LOG'] else Environment.SERVER['LOG']['LEVEL']
            )
    except KeyError as e:
        pass
    except FileNotFoundError as e:
        pass
    logging.debug("Configuration file loaded...")
    base_app = BaseApp()
    base_app.load_app()
    Process.start(args)


if __name__ == '__main__':
    main()
