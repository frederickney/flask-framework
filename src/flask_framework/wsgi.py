#!/usr/bin/python3
# coding: utf-8


__author__ = 'Frederick NEY'

import argparse
import logging
import os
import sys

try:
    import eventlet
    eventlet.monkey_patch(all=True)
except ImportError as e:
    pass

try:
    from gunicorn.app.base import Application as WSGIServer
    try:
        import gevent.monkey
        gevent.monkey.patch_all()
    except ImportError as e:
        pass
except ImportError:
    from waitress.server import WSGIServer
from six import iteritems

from flask_framework.config import Environment
from flask_framework.core import Process
from flask_framework.core.logging import setup_file_logging, configure_basic_logger
from flask_framework.common import Logging
from flask_framework.common import BaseApp
from flask_framework.core.process import number_of_workers

parser = argparse.ArgumentParser(description='Python FLASK USGI server')
parser.add_argument(
    '-d', '--disable-log-files',
    action='store_true',
    required=False,
    help='Deactivate logs to file'
)


class Server(WSGIServer, BaseApp):

    def init(self, parser, opts, args):
        print(parser)
        print(opts)
        print(args)

    def __init__(self, options=None):
        Server.options = (options or {}) if not hasattr(Server, 'options') else Server.options
        BaseApp.__init__(self)
        Server.load_app()
        self.application = Process.get()
        try:
            super(Server, self).__init__()
        except TypeError as e:
            super(Server, self).__init__(
                self.application,
                host=Environment.SERVER['BIND']['ADDRESS'],
                port=Environment.SERVER['BIND']['PORT'],
                threads=number_of_workers(),
            )

    def reload(self):
        """
        reload app function
        :return:
        """
        logging.info('reloading')
        try:
            import gevent.monkey
            gevent.monkey.patch_all()
        except ImportError as e:
            pass
        Environment.reload(os.environ['CONFIG_FILE'])
        Server.load_app()
        self.application = Process.get()
        Server.load_options()
        super(Server, self).reload()

    def load_config(self):
        """
        Load gunicorn options
        """
        logging.info(Server.options)
        config = dict(
            [(key, value) for key, value in iteritems(Server.options) if key in self.cfg.settings and value is not None]
        )
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        """
        Load app for gunicorn.

        Called on gunicorn.load event
        """
        try:
            import eventlet
            eventlet.monkey_patch(all=True)
        except ImportError as e:
            pass
        try:
            import eventlet
            eventlet.monkey_patch(all=True)
        except ImportError as e:
            pass
        return self.application

    @classmethod
    def load_options(cls):
        cls.options = {
            'bind': '%s:%i' % (Environment.SERVER['BIND']['ADDRESS'], Environment.SERVER['BIND']['PORT']),
            'workers': number_of_workers(),
            'threads': Environment.SERVER['THREADS_PER_CORE'],
            'capture_output': Environment.SERVER['CAPTURE'],
            "loglevel": Logging.get_loglevel(),
            "worker_class": Environment.SERVER['WORKERS'],
            "reload_engine": 'poll'
        }
        if Logging.logging_dir_exist:
            cls.options["errorlog"] = os.path.join(os.environ.get("log_dir"), 'flask-error.log')
            cls.options["accesslog"] = os.path.join(os.environ.get("log_dir"), 'flask-access.log')
        if 'SSL' in Environment.SERVER:
            cls.options["certfile"] = Environment.SERVER['SSL']['Certificate']
            cls.options["keyfile"] = Environment.SERVER['SSL']['PrivateKey']


def start(args):
    """
    Loads options and starts process.
    :param args:
    :type args: argparse.Namespace
    """
    logging.info("Loading options...")
    Server.load_options()
    logging.info("Options loaded...")
    logging.info("Starting the server...")
    try:
        Server().run()
    except RuntimeError as e:
        exit(255)


def main():
    """"
    main entrypoint for flask_framework.wsgi
    loads environments and setups loging handler
    """
    if os.getcwd() not in sys.path:
        sys.path.append(os.getcwd())
    args = parser.parse_args()
    configure_basic_logger(None)
    if not args.disable_log_files:
        setup_file_logging()
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
    logging.info("Loading configuration file...")
    Environment.load(os.environ['CONFIG_FILE'])
    logging.info("Configuration file loaded...")
    try:
        Logging.set_loglevel(Environment.SERVER['LOG']['LEVEL'])
        configure_basic_logger(level=Environment.SERVER['LOG']['LEVEL'])
    except KeyError as e:
        logging.error(e)
        pass
    Logging.logging_dir_exist = False
    try:
        if not args.disable_log_files:
            os.environ.setdefault('LOG_DIR', Environment.SERVER['LOG']['DIR'])
            setup_file_logging(level=Environment.SERVER['LOG']['LEVEL'])
        logging.info('Logging handler initialized')
    except KeyError as e:
        pass
    except FileNotFoundError as e:
        pass
    except PermissionError as e:
        pass
    start(args)


if __name__ == '__main__':
    main()
