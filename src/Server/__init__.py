# coding: utf-8

__author__ = 'Frederick NEY'

from . import WS, Web, ErrorHandler
from flask_sessions import Session


def configure_logs(name, format, output_file, debug='info'):
    import logging
    logger = logging.getLogger(name)
    formatter = logging.Formatter(format)
    file_handler = logging.FileHandler(output_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logging.getLevelName(debug.upper())
    logger.setLevel(logging.getLevelName(debug.upper()))


class Process(object):

    _app = None
    _process = None
    _scheduler = None
    _pidfile = "/run/rh-bot-srv.pid"

    @classmethod
    def init(cls, tracking_mode=False):
        from flask import Flask
        from Config import Environment
        cls._app = Flask(
            Environment.SERVER_DATA['APP_NAME'],
            static_url_path="/file",
            static_folder=Environment.SERVER_DATA['STATIC_PATH'],
            template_folder=Environment.SERVER_DATA['TEMPLATE_PATH']
        )
        if 'APP_KEY' in Environment.SERVER_DATA:
            cls._session = Session()
            cls._app.config['SECRET_KEY'] = Environment.SERVER_DATA['APP_KEY']
            cls._app.config['SESSION_TYPE'] = 'filesystem'
            cls._app.config['SESSION_FILE_DIR'] = Environment.SERVER_DATA['SESSION_FILE_DIR']
            cls._session.init_app(cls._app)
        cls._app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = tracking_mode
        return cls._app

    @classmethod
    def start(cls, args):
        cls._args = args
        from flask_apscheduler import APScheduler
        from werkzeug.serving import make_server, make_ssl_devcert
        from gevent.pywsgi import WSGIServer
        cls._scheduler = APScheduler()
        if 'JOBS' not in cls._app.config:
            cls._app.config['JOBS'] = []
        if 'SCHEDULER_API_ENABLED' not in cls._app.config:
            cls._app.config['SCHEDULER_API_ENABLED'] = False
        if args.listening_address is not None:
            cls._scheduler.init_app(cls._app)
            cls._scheduler.start()
            #logger.info("Starting listening on " + args.listening_address + " on port " + args.listening_port)
            print("Starting listening on %s on port %d" % (args.listening_address, int(args.listening_port)))
            if args.debug:
                cls._app.run(host=args.listening_address, port=int(args.listening_port), debug=args.debug)
            else:
                try:
                    if args.pid:
                        cls.pid()
                    cls._server = WSGIServer((args.listening_address, int(args.listening_port)), cls._app)
                    cls._server.serve_forever()
                finally:
                    if args.pid:
                        cls.shutdown()
        else:
            cls._scheduler.init_app(cls._app)
            cls._scheduler.start()
            #logger.info("Starting listening on 0.0.0.0 on port " + args.listening_port)
            print("Starting listening on 0.0.0.0 on port %d" % int(args.listening_port))
            if args.debug:
                cls._app.run(host="0.0.0.0", port=int(args.listening_port), debug=args.debug)
            else:
                try:
                    if args.pid:
                        cls.pid()
                    cls._server = WSGIServer(("0.0.0.0", int(args.listening_port)), cls._app)
                    cls._server.serve_forever()
                finally:
                    if args.pid:
                        cls.shutdown()
        #logger.info("Server is running")

    @classmethod
    def wsgi_setup(cls):
        from flask_apscheduler import APScheduler
        cls._scheduler = APScheduler()
        if 'JOBS' not in cls._app.config:
            cls._app.config['JOBS'] = []
        if 'SCHEDULER_API_ENABLED' not in cls._app.config:
            cls._app.config['SCHEDULER_API_ENABLED'] = False
        cls._scheduler.init_app(cls._app)
        cls._scheduler.start()
        return cls._app

    @classmethod
    def load_routes(cls):
        WS.Route(cls._app)
        Web.Route(cls._app)
        ErrorHandler.Route(cls._app)

    @classmethod
    def add_task(cls, function, args=(), trigger='interval', seconds=0, minutes=0, hours=0, days=0, weeks=0):
        if 'JOBS' not in cls._app.config:
            cls._app.config['JOBS'] = []
        jobs = cls._app.config['JOBS']
        task = {
            "id": function,
            "func": function.replace('.', ':', 1),
            'args': args,
            'trigger': trigger,
        }
        if seconds == 0 and minutes == 0 and hours == 0 and days == 0 and weeks == 0:
            seconds = 1
        if seconds != 0:
            task["seconds"] = seconds
        elif minutes != 0:
            task["minutes"] = minutes
        elif hours != 0:
            task["hours"] = hours
        elif days != 0:
            task["days"] = days
        jobs.append(task)
        cls._app.config['JOBS'] = jobs
        if 'SCHEDULER_API_ENABLED' not in cls._app.config:
            cls._app.config['SCHEDULER_API_ENABLED'] = True

    @classmethod
    def pid(cls):
        import os
        import sys
        pid = str(os.getpid())
        if os.path.isfile(cls._pidfile):
            print("%s already exists, exiting" % cls._pidfile)
            sys.exit()
        pid_file = open(cls._pidfile, 'w')
        pid_file.write(pid)
        pid_file.close()

    @classmethod
    def shutdown(cls):
        import os
        os.unlink(cls._pidfile)

    @classmethod
    def stop(cls, code=0):
        if cls._args.pid:
            cls.shutdown()
        exit(code)
