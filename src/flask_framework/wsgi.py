#!/usr/bin/python3
# coding: utf-8


__author__ = 'Frederick NEY'


import multiprocessing

import gevent.monkey
import gunicorn.app.base
from six import iteritems


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
        import flask_framework.Task as Task
        import flask_framework.Extensions as Extensions
        logging.info("Initializing the server...")
        Process.init(tracking_mode=False)
        logging.info("Server initialized...")
        logging.debug("Loading server routes...")
        Process.load_routes()
        Process.load_middleware()
        Extensions.load()
        Extensions.load()
        logging.debug("Server routes loaded...")
        logging.debug("Loading websocket events")
        Process.load_socket_events()
        logging.debug("Websocket events loaded...")
        # app.teardown_appcontext(Database.save)
        logging.info("Server started...")
        return Process.wsgi_setup()

    def __init__(self, options=None):
        self.options = options or {}
        self.application = Server.application()
        super(Server, self).__init__()

    def reload(self):
        """
        reload app function
        :return:
        """
        logging.info('reloading')
        self.prog = Server.application()
        super(Server, self).reload()

    def load_config(self):
        config = dict([(key, value) for key, value in iteritems(self.options)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application




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
    logging.info("Configuration file loaded...")
    try:
        loglevel = Environment.SERVER_DATA['LOG']['LEVEL']
        logging.getLogger().setLevel(loglevel.upper())
    except KeyError as e:
        pass
    logging_dir_exist = False
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
        os.environ.setdefault("log_dir", Environment.SERVER_DATA["LOG"]["DIR"])
        logging_dir_exist = True
    except KeyError as e:
        pass
    except FileNotFoundError as e:
        pass
    logging.info("Loading options...")
    options = {
        'bind': '%s:%i' % (Environment.SERVER_DATA['BIND']['ADDRESS'], Environment.SERVER_DATA['BIND']['PORT']),
        'workers': Server.number_of_workers(),
        'threads': Environment.SERVER_DATA['THREADS_PER_CORE'],
        'capture_output': Environment.SERVER_DATA['CAPTURE'],
        "loglevel": loglevel,
        "worker_class": Environment.SERVER_DATA['WORKERS'],
    }
    if logging_dir_exist:
        options["errorlog"] = os.path.join(os.environ.get("log_dir"), 'flask-error.log')
        options["accesslog"] = os.path.join(os.environ.get("log_dir"), 'flask-access.log')
    if 'SSL' in Environment.SERVER_DATA:
        options["certfile"] = Environment.SERVER_DATA['SSL']['Certificate']
        options["keyfile"] = Environment.SERVER_DATA['SSL']['PrivateKey']
    logging.info("Options loaded...")
    if 'default' in Environment.Databases:
        logging.debug("Connecting to default database...")
        from flask_framework.Database import Database
        Database.register_engines()
        Database.init()
        logging.debug("Default database connected...")

    logging.info("Starting the server...")
    Server(options).run()
