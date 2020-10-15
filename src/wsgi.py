#!/usr/bin/python3
# coding: utf-8

__author__ = 'Frederick NEY'

import multiprocessing
import gunicorn.app.base
from six import iteritems

import gevent.monkey
gevent.monkey.patch_all()

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
        import Extensions
        logging.info("Initializing the server...")
        Process.init(tracking_mode=False)
        logging.info("Server initialized...")
        #Process.init_sheduler()
        logging.debug("Loading server routes...")
        Process.load_routes()
        Process.load_middleware()
        Extensions.load()
        logging.debug("Server routes loaded...")
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

    logging.basicConfig(
        level=loglevel.upper(),
        format='[%(asctime)s] [%(levelname)s]: %(message)s',
        filename=os.environ.get('log_file')
    )
    logging.info("Configuration file loaded...")
    logging.info("Loading options...")
    options = {
        'bind': '%s:%i' % (Environment.SERVER_DATA['BIND']['ADDRESS'], Environment.SERVER_DATA['BIND']['PORT']),
        'workers': Server.number_of_workers(),
        'threads': Environment.SERVER_DATA['THREADS_PER_CORE'],
        'capture_output': Environment.SERVER_DATA['CAPTURE'],
        "errorlog": os.path.join(os.environ.get("log_dir"), 'flask-error.log'),
        "accesslog": os.path.join(os.environ.get("log_dir"), 'flask-access.log'),
        "loglevel": loglevel,
        "worker_class": 'geventwebsocket.gunicorn.workers.GeventWebSocketWorker',
    }
    logging.info("Options loaded...")

    logging.debug("Connecting database(s)...")
    from Database import Database
    Database.register_engines()
    Database.init()
    logging.debug("Database(s) connected...")

    logging.info("Starting the server...")
    Server(options).run()

