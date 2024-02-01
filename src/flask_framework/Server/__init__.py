# coding: utf-8


__author__ = 'Frederick NEY'


import apscheduler.jobstores.redis
import functools
import warnings
from . import WS, Web, ErrorHandler, Middleware,  RequestHandler, Socket
from flask_session import Session
from datetime import datetime, timedelta
from flask import Flask
from flask_apscheduler import APScheduler


def configure_logs(name, format, output_file, debug='info'):
    """

    :param name:
    :type name: str
    :param format:
    :type format: str
    :param output_file:
    :type output_file: str
    :param debug:
    :type debug: str
    :return:
    """
    import logging
    logger = logging.getLogger(name)
    formatter = logging.Formatter(format)
    file_handler = logging.FileHandler(output_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logging.getLevelName(debug.upper())
    logger.setLevel(logging.getLevelName(debug.upper()))


class Process(object):

    _app: Flask = None
    _scheduler: APScheduler = None
    _pidfile = "/run/flask.pid"
    _socket = None
    sso = None
    openid = None
    ldap = None

    @classmethod
    def init(cls, tracking_mode=False):
        """

        :param tracking_mode:
        :type tracking_mode: bool
        :return:
        :rtype: flask.Flask
        """
        import os.path
        import pathlib
        from flask_socketio import SocketIO
        from flask import Flask
        from flask_framework.Config import Environment
        cls._app = Flask(
            Environment.SERVER_DATA['APP_NAME'],
            static_url_path="/file",
            static_folder=
            Environment.SERVER_DATA['STATIC_PATH']
            if 'STATIC_PATH' in Environment.SERVER_DATA
            else os.path.join(pathlib.Path(__file__).resolve().parent.resolve().parent, 'static'),
            template_folder=
            Environment.SERVER_DATA['TEMPLATE_PATH']
            if 'TEMPLATE_PATH' in Environment.SERVER_DATA
            else os.path.join(pathlib.Path(__file__).resolve().parent.resolve().parent, 'template')
        )
        if 'CONFIG' in Environment.FLASK:
            if Environment.FLASK['CONFIG'] is not None:
                cls._app.config.update(Environment.FLASK['CONFIG'])
        if 'APP_KEY' in Environment.SERVER_DATA:
            from flask_wtf.csrf import CSRFProtect
            cls._session = Session()
            #cls._app.config['TESTING'] = True
            #cls._app.config['TEMPLATES_AUTO_RELOAD'] = True
            cls._app.config['SECRET_KEY'] = Environment.SERVER_DATA['APP_KEY']
            cls._app.config['SESSION_TYPE'] = Environment.SERVER_DATA['SESSION']
            if Environment.SERVER_DATA['SESSION'] == 'filesystem':
                cls._app.config['SESSION_FILE_DIR'] = Environment.Services[Environment.SERVER_DATA['SESSION']]['PATH']
            if Environment.SERVER_DATA['SESSION'] == 'memcached':
                import pymemcache
                cls._app.config['SESSION_MEMCACHED'] = pymemcache.Client(
                    (
                        Environment.Services[Environment.SERVER_DATA['SESSION']]['HOST'],
                        Environment.Services[Environment.SERVER_DATA['SESSION']]['PORT']
                    )
                )
            if Environment.SERVER_DATA['SESSION'] == 'redis':
                import redis
                cls._app.config['SESSION_REDIS'] = redis.from_url("%s://%s:%d/redis" % (
                        Environment.SERVER_DATA['SESSION'],
                        Environment.Services[Environment.SERVER_DATA['SESSION']]['HOST'],
                        Environment.Services[Environment.SERVER_DATA['SESSION']]['PORT']
                    )
                )
            if Environment.SERVER_DATA['SESSION'] == 'sqlalchemy':
                from flask_framework.Database import Database
                cls._app = Database.setup_sessions(
                    cls._app
                )
            if Environment.SERVER_DATA['SESSION'] == 'mongodb':
                from pymongo import MongoClient
                db_conf = Environment.Databases[Environment.SERVER_DATA['SESSION']]
                cls._app.config['SESSION_MONGODB'] = MongoClient(
                    "%s://%s:%s@%s:%d" % (
                        db_conf['driver'],
                        db_conf['user'],
                        db_conf['password'],
                        db_conf['address'],
                        db_conf['port']
                    )
                )
                cls._app.config['SESSION_MONGODB_DB'] = db_conf['database']
                cls._app.config['SESSION_MONGODB_COLLECT'] = db_conf['collection']
            cls._session.init_app(cls._app)
            cls._csrf = CSRFProtect()
            cls._csrf.init_app(cls._app)
            if 'SSO' in Environment.Logins:
                from flask_sso import SSO
                cls.sso = SSO()
                cls.sso.init_app(cls._app)
            if 'OpenID' in Environment.Logins:
                from Utils.Auth.openid import OpenIDConnect
                from flask_openid import OpenID
                cls.openid = OpenIDConnect()
                cls.openid.init_app(cls._app)
            if 'SAML2' in Environment.Logins:
                import flask_saml
                cls.saml = flask_saml.FlaskSAML()
                cls._csrf.exempt("flask_saml.login_acs")
                cls._csrf.exempt("flask_saml.login")
                cls._csrf.exempt("flask_saml.logout")
                cls._csrf.exempt("flask_saml.metadata")
                cls.saml.init_app(cls._app)
            if 'LDAP' in Environment.Logins:
                if 'LDAP_HOST' not in Environment.Logins['LDAP'] and 'LDAP_DOMAIN' in Environment.Logins['LDAP']:
                    from activedirectory import Locator
                    ldap = Locator()
                    Environment.Logins['LDAP']['LDAP_HOST'] = ldap.locate_many(
                        Environment.Logins['LDAP']['LDAP_DOMAIN']
                    )[0]
                if 'LDAP_REQUIRED_GROUP' not in Environment.Logins['LDAP']:
                    Environment.Logins['LDAP']['LDAP_REQUIRED_GROUP'] = None
                from flask_framework.Utils.Auth.ldap import LDAP
                for key, val in Environment.Logins['LDAP'].items():
                    cls._app.config[key] = val
                cls.ldap = LDAP(cls._app)
        cls._socket = SocketIO()
        cls._socket.init_app(cls._app)
        return cls._app

    @classmethod
    def instanciate(cls):
        """
            :param
            args:
            :return:
        """
        import logging
        from  flask_framework.Config import Environment
        from flask_apscheduler import APScheduler
        from werkzeug.serving import make_server, make_ssl_devcert
        from gevent.pywsgi import WSGIServer
        cls._scheduler = APScheduler()
        if 'JOBS' not in cls._app.config:
            cls._app.config['JOBS'] = []
        if 'SCHEDULER_API_ENABLED' not in cls._app.config:
            cls._app.config['SCHEDULER_API_ENABLED'] = False
            cls._scheduler.init_app(cls._app)
            cls._scheduler.start()
            #logger.info("Starting listening on " + args.listening_address + " on port " + args.listening_port)
        return cls._app

    @classmethod
    def start(cls, args):
        """

        :param args:
        :return:
        """
        cls._args = args
        from flask_apscheduler import APScheduler
        from werkzeug.serving import make_server, make_ssl_devcert
        from gevent.pywsgi import WSGIServer
        from flask_framework.Config import Environment
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
            if 'SSL' in Environment.SERVER_DATA:
                if args.debug:
                    cls._app.run(host=args.listening_address, port=int(args.listening_port), debug=args.debug, ssl_context=(Environment.SERVER_DATA['SSL']['Certificate'], Environment.SERVER_DATA['SSL']['PrivateKey']))
                else:
                    try:
                        if args.pid:
                            cls.pid()
                        cls._server = WSGIServer((args.listening_address, int(args.listening_port)), cls._app,  keyfile=Environment.SERVER_DATA['SSL']['PrivateKey'], certfile=Environment.SERVER_DATA['SSL']['Certificate'])
                        cls._server.serve_forever()
                    finally:
                        if args.pid:
                            cls.shutdown()
            else:
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
            if 'SSL' in Environment.SERVER_DATA:
                if args.debug:
                    cls._app.run(host="0.0.0.0", port=int(args.listening_port), debug=args.debug, ssl_context=(Environment.SERVER_DATA['SSL']['Certificate'], Environment.SERVER_DATA['SSL']['PrivateKey']))
                else:
                    try:
                        if args.pid:
                            cls.pid()
                        cls._server = WSGIServer(("0.0.0.0", int(args.listening_port)), cls._app,  keyfile=Environment.SERVER_DATA['SSL']['PrivateKey'], certfile=Environment.SERVER_DATA['SSL']['Certificate'])
                        cls._server.serve_forever()
                    finally:
                        if args.pid:
                            cls.shutdown()
            else:
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
        """

        :return:
        :rtype: flask.Flask
        """
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
    def load_socket_events(cls):
        if cls._socket is not None:
            Socket.Handler(cls._socket)


    @classmethod
    def load_routes(cls):
        """

        :return:
        """
        RequestHandler.Init(cls._app)
        WS.Route(cls._app)
        Web.Route(cls._app)
        ErrorHandler.Route(cls._app)

    @classmethod
    def load_middleware(cls):
        """

        :return:
        """
        Middleware.Load(cls._app)

    @classmethod
    def get_ws(cls):
        return cls._socket

    @classmethod
    def add_task(cls, function, id=None, args=(), trigger='interval', seconds=0, minutes=0, hours=0, days=0, weeks=0):
        """

        :param function:
        :type function: str
        :param id:
        :type id: str
        :param args:
        :type args: tuple
        :param trigger:
        :type trigger: str
        :param seconds:
        :type seconds: int
        :param minutes:
        :type minutes: int
        :param hours:
        :type hours: int
        :param days:
        :type days: int
        :param weeks:
        :type weeks: int
        :return:
        """
        from flask_framework.Config import Environment
        if 'JOBS' not in cls._app.config:
            cls._app.config['JOBS'] = []
        jobs = cls._app.config['JOBS']
        task = {
            "id": id if id is not None else function,
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
            cls._app.config['SCHEDULER_JOBSTORES']= {
                'default': apscheduler.jobstores.redis.RedisJobStore(
                    port = Environment.Services['redis']['PORT'],
                    host = Environment.Services['redis']['HOST'],
                    db=10
                )
            }
            cls._app.config['SCHEDULER_API_ENABLED'] = True

    @classmethod
    def add_cron(cls, function, id=None, args=(), trigger='interval', seconds=0, minutes=0, hours=0, days=0, weeks=0):
        """

        :param function:
        :type function: str
        :param id:
        :type id: str
        :param args:
        :type args: tuple
        :param trigger:
        :type trigger: str
        :param seconds:
        :type seconds: int
        :param minutes:
        :type minutes: int
        :param hours:
        :type hours: int
        :param days:
        :type days: int
        :param weeks:
        :type weeks: int
        :return:
        """
        from flask_framework.Config import Environment
        if seconds == 0 and minutes == 0 and hours == 0 and days == 0 and weeks == 0:
            seconds = 1
        cls._scheduler.add_job(id=id if id is not None else function, func=function.replace('.', ':', 1), args=args, trigger=trigger, hours=hours, minutes=minutes, seconds=seconds, days=days)
        if 'SCHEDULER_API_ENABLED' not in cls._app.config:
            cls._app.config['SCHEDULER_API_ENABLED'] = True

    @classmethod
    def add_parallel_task(cls, function, id=None, args=(), trigger='date', date=datetime.now() + timedelta(0, 0)):
        """

        :param function:
        :type function: str
        :param id:
        :type id: str
        :param args:
        :type args: tuple
        :param trigger:
        :type trigger: str
        :param date:
        :type date: datetime.datetime
        :return:
        """
        cls._scheduler.add_job(id=function, func=function.replace('.', ':', 1), args=args, trigger=trigger, run_date=date)
        cls._scheduler.run_job(id=id if id is not None else function)
        if 'SCHEDULER_API_ENABLED' not in cls._app.config:
            cls._app.config['SCHEDULER_API_ENABLED'] = True

    @classmethod
    def pid(cls):
        """

        :return:
        """
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
        """

        :return:
        """
        import os
        os.unlink(cls._pidfile)

    @classmethod
    def get(cls):
        """

        :return:
        :rtype: flask.Flask
        """
        return cls._app

    @classmethod
    def stop(cls, code=0):
        """

        :param code:
        :type: int
        :return:
        """
        if cls._args.pid:
            cls.shutdown()
        exit(code)

    @classmethod
    def init_sheduler(cls):
        from flask_framework.Config import Environment
        if 'JOBS' not in cls._app.config:
            cls._app.config['JOBS'] = []
        cls._app.config['SCHEDULER_API_ENABLED'] = True
        cls._app.config['SCHEDULER_JOBSTORES'] = {
            'default': apscheduler.jobstores.redis.RedisJobStore(
                port=Environment.Services['redis']['PORT'],
                host=Environment.Services['redis']['HOST'],
                db=10
            )
        }
        return


class WebDenyFunctionCall(DeprecationWarning):

    """
    Base class for disabling call of function.
    """
    def __init__(self, *args, **kwargs): # real signature unknown
        super(WebDenyFunctionCall, self).__init__(*args, **kwargs)

    @staticmethod # known case of __new__
    def __new__(*args, **kwargs): # real signature unknown
        """ Create and return a new object.  See help(type) for accurate signature. """
        return args[1]


def deniedwebcall(func):
    """Deprecation decorator which can be used to mark functions / classes
    as deprecated. It will result in a warning being emitted
    when the function is used."""
    @functools.wraps(func)
    def deny(*args, **kwargs):
        import logging
        from flask import redirect
        from flask import request
        from flask import url_for
        if len(dir(request)) != 0:
            warnings.simplefilter('always', WebDenyFunctionCall)  # turn off filter
            warnings.warn("Access denied to function %s." % func.__name__, category=WebDenyFunctionCall, stacklevel=2)
            warnings.simplefilter('default', WebDenyFunctionCall)  # reset filter
            return redirect(request.referrer or url_for('home'))
        return func(*args, **kwargs)

    return deny
