#!/usr/bin/python3
# coding: utf-8


__author__ = 'Frederick NEY'

try:
    import gevent.monkey

    gevent.monkey.patch_all()
except ImportError as e:
    pass
try:
    import eventlet

    eventlet.monkey_patch(all=True)
except ImportError as e:
    pass

import multiprocessing

import gunicorn.app.base
from six import iteritems

from flask_framework.Database import Database


class Server(gunicorn.app.base.Application):

    def init(self, parser, opts, args):
        print(parser)
        print(opts)
        print(args)

    @staticmethod
    def number_of_workers():
        return multiprocessing.cpu_count() * 2

    @staticmethod
    def application():
        import logging
        from flask_framework.Server import Process
        import flask_framework.Extensions as Extensions
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
        # app.teardown_appcontext(Database.save)
        Extensions.load()
        logging.info("Server started...")
        return Process.wsgi_setup()

    def __init__(self, options=None):
        Server.options = (options or {}) if not hasattr(Server, 'options') else Server.options
        self.application = Server.application()
        super(Server, self).__init__()

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
        self.application = Server.application()
        Server.load_options()
        super(Server, self).reload()

    def load_config(self):
        logging.info(Server.options)
        config = dict([(key, value) for key, value in iteritems(Server.options)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
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
            'bind': '%s:%i' % (Environment.SERVER_DATA['BIND']['ADDRESS'], Environment.SERVER_DATA['BIND']['PORT']),
            'workers': Server.number_of_workers(),
            'threads': Environment.SERVER_DATA['THREADS_PER_CORE'],
            'capture_output': Environment.SERVER_DATA['CAPTURE'],
            "loglevel": loglevel,
            "worker_class": Environment.SERVER_DATA['WORKERS'],
            "reload_engine": 'poll'
        }
        if logging_dir_exist:
            cls.options["errorlog"] = os.path.join(os.environ.get("log_dir"), 'flask-error.log')
            cls.options["accesslog"] = os.path.join(os.environ.get("log_dir"), 'flask-access.log')
        if 'SSL' in Environment.SERVER_DATA:
            cls.options["certfile"] = Environment.SERVER_DATA['SSL']['Certificate']
            cls.options["keyfile"] = Environment.SERVER_DATA['SSL']['PrivateKey']


if __name__ == '__main__':
    import os
    import flask_framework.Server as Process
    import logging
    from logging.handlers import TimedRotatingFileHandler
    from flask_framework.Config import Environment

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
    Server.load_options()
    logging.info("Options loaded...")
    if 'default' in Environment.Databases:
        logging.debug("Connecting to default database...")
        Database.register_engines(echo=Environment.SERVER_DATA['CAPTURE'])
        Database.init()
        logging.debug("Default database connected...")
    logging.info("Starting the server...")
    Server().run()
