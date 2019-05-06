# coding: utf-8

__author__ = 'Frederick NEY'

from . import WS, Web, ErrorHandler


def configure_logs(name, format, output_file, debug=False):
    import logging
    logger = logging.getLogger(name)
    formatter = logging.Formatter(format)
    file_handler = logging.FileHandler(output_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)


class Process(object):

    _app = None
    _process = None
    _scheduler = None

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
        db_conf = Environment.Databases['default']
        cls._app.config['MYSQL_HOST'] = db_conf['address']
        cls._app.config['MYSQL_USER'] = db_conf['user']
        cls._app.config['MYSQL_PASSWORD'] = db_conf['password']
        cls._app.config['MYSQL_DB'] = db_conf['database']
        cls._app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = tracking_mode
        return cls._app

    @classmethod
    def start(cls, args):
        from flask_apscheduler import APScheduler
        from werkzeug.serving import make_server, make_ssl_devcert
        if args.listening_address is not None:
            cls._scheduler = APScheduler()
            if 'JOBS' not in cls._app.config:
                cls._app.config['JOBS'] = []
            if 'SCHEDULER_API_ENABLED' not in cls._app.config:
                cls._app.config['SCHEDULER_API_ENABLED'] = False
            cls._scheduler.init_app(cls._app)
            cls._scheduler.start()
            #logger.info("Starting listening on " + args.listening_address + " on port " + args.listening_port)
            print("Starting listening on %s on port %d" % (args.listening_address, int(args.listening_port)))
            cls._app.run(host=args.listening_address, port=int(args.listening_port), debug=args.debug)
        else:
            cls._scheduler = APScheduler()
            cls._scheduler.init_app(cls._app)
            cls._scheduler.start()
            #logger.info("Starting listening on 0.0.0.0 on port " + args.listening_port)
            print("Starting listening on 0.0.0.0 on port %d" % int(args.listening_port))
            cls._app.run(host="0.0.0.0", port=int(args.listening_port), debug=args.debug)
        #logger.info("Server is running")

    @classmethod
    def load_routes(cls):
        WS.Route(cls._app)
        Web.Route(cls._app)
        ErrorHandler.Route(cls._app)

    @classmethod
    def add_task(cls, function, args=(), trigger='interval', second=1):
        if 'JOBS' not in cls._app.config:
            cls._app.config['JOBS'] = []
        jobs = cls._app.config['JOBS']
        jobs.append({
            "id": function,
            "func": function.replace('.', ':', 1),
            'args': args,
            'trigger': trigger,
            'seconds': second
        })
        cls._app.config['JOBS'] = jobs
        if 'SCHEDULER_API_ENABLED' not in cls._app.config:
            cls._app.config['SCHEDULER_API_ENABLED'] = True