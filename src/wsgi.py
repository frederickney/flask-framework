#!/usr/bin/python3
# coding: utf-8

__author__ = 'Frederick NEY'

import multiprocessing
import gunicorn.app.base
from gunicorn.six import iteritems


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
        from Server import Process
        import Task
        logger = logging.getLogger('GLOBAL')
        logger.info("Initializing the server...")
        Process.init(tracking_mode=False)
        logger.info("Server initialized...")
        logger.debug("Loading server routes...")
        Process.load_routes()
        logger.debug("Server routes loaded...")
        # app.teardown_appcontext(Database.save)

        logger.info("Server started...")
        return Process.wsgi_setup()

    def __init__(self, options=None):
        self.options = options or {}
        self.application = Server.application()
        super(Server, self).__init__()

    def load_config(self):
        config = dict([(key, value) for key, value in iteritems(self.options)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


if __name__ == '__main__':
    import os
    import Server as Process
    import logging
    from Config import Environment
    loglevel = 'info'
    os.environ.setdefault("log_dir", os.environ.get("LOG_DIR", "/var/log/server/"))
    os.environ.setdefault("log_file", os.path.join(os.environ.get("log_dir"), 'process.log'))
    if 'CONFIG_FILE' in os.environ:
        Environment.load(os.environ['CONFIG_FILE'])
    else:
        Environment.load("/etc/server/config.json")
    loglevel = Environment.SERVER_DATA['LOG_LEVEL']
    Process.configure_logs(
        'GLOBAL',
        '[%(asctime)s] [%(levelname)s]: %(message)s',
        os.environ.get("log_file"),
        loglevel
    )
    logger = logging.getLogger('GLOBAL')
    logger.info("Configuration file loaded...")
    logger.info("Loading options...")
    options = {
        'bind': '%s:%i' % (Environment.SERVER_DATA['BIND']['ADDRESS'], Environment.SERVER_DATA['BIND']['PORT']),
        'workers': Server.number_of_workers(),
        'threads': Environment.SERVER_DATA['THREADS_PER_CORE'],
        'capture_output': Environment.SERVER_DATA['CAPTURE'],
        "errorlog": os.path.join(os.environ.get("log_dir"), 'flask-error.log'),
        "accesslog": os.path.join(os.environ.get("log_dir"), 'flask-access.log'),
        "loglevel": loglevel,
        "worker_class": 'sync'
    }
    logger.info("Options loaded...")

    if 'default' in Environment.Databases:
        logger.debug("Connecting to default database...")
        from Database import Database
        db_conf = Environment.Databases['default']
        Database.setup(
            db_conf['driver'], db_conf['user'], db_conf['password'], db_conf['address'], db_conf['database'],
        )
        Database.init()
        logger.debug("Default database connected...")

    logger.info("Starting the server...")
    Server(options).run()

