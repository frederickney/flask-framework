# coding: utf-8


__author__ = 'Frederick NEY'

import os
import pathlib
import sys
from datetime import datetime, timedelta

import apscheduler.jobstores.redis
from flask import Flask
from flask_apscheduler import APScheduler
from flask_session import Session
from flask_socketio import SocketIO
from gevent.pywsgi import WSGIServer

from flask_framework.config import Environment
from . import errors
from . import handler
from . import middleware
from . import plugins
from . import socket
from . import web
from . import ws


class Process(object):
    """
        Core class ot the framework, handles all fastapi configuration / registration

        Contains following attributes:
        Attributes
        ----------
            sso: SSO
                for handling user authentication both in swagger and endpoints uses flask_sso.SSO
            openid: FlaskOIDC
                for handling user authentication both in swagger and endpoints uses flask_login_oidc.FlaskOIDC
            saml: FlaskSAML
                for handling user authentication both in swagger and endpoints uses flask_login_saml.FlaskSAML
        """
    _app: Flask = None
    _scheduler: APScheduler = None
    _pidfile = "/run/flask.pid"
    _socket = None
    _login_manager = None
    _csrf = None
    sso = None
    openid = None
    saml = None

    @classmethod
    def init(cls, tracking_mode=False):
        """
        Initialize the framework and creates flask instances with others plugins based on configuration
        :param tracking_mode:
        :type tracking_mode: bool
        :return:
        :rtype: flask.Flask
        """
        cls._app = Flask(
            Environment.SERVER['APP_NAME'],
            static_url_path="/file",
            static_folder=(
                os.path.abspath(Environment.SERVER['STATIC_PATH'] if 'STATIC_PATH' in Environment.SERVER else
                                os.path.join(pathlib.Path(__file__).resolve().parent.resolve().parent, 'static'))
            ),
            template_folder=(
                os.path.abspath(Environment.SERVER['TEMPLATE_PATH'] if 'TEMPLATE_PATH' in Environment.SERVER else
                                os.path.join(pathlib.Path(__file__).resolve().parent.resolve().parent, 'template'))
            )
        )
        if 'CONFIG' in Environment.FLASK:
            if Environment.FLASK['CONFIG'] is not None:
                cls._app.config.update(Environment.FLASK['CONFIG'])
        if 'APP_KEY' in Environment.SERVER:
            from flask_wtf.csrf import CSRFProtect
            cls._session = Session()
            # cls._app.config['TESTING'] = True
            # cls._app.config['TEMPLATES_AUTO_RELOAD'] = True
            cls._app.config['SECRET_KEY'] = Environment.SERVER['APP_KEY']
            cls._app.config['SESSION_TYPE'] = Environment.SERVER['SESSION']
            if Environment.SERVER['SESSION'] == 'filesystem':
                cls._app.config['SESSION_FILE_DIR'] = Environment.Services[Environment.SERVER['SESSION']]['PATH']
            if Environment.SERVER['SESSION'] == 'memcached':
                import pymemcache
                cls._app.config['SESSION_MEMCACHED'] = pymemcache.Client(
                    (
                        Environment.Services[Environment.SERVER['SESSION']]['HOST'],
                        Environment.Services[Environment.SERVER['SESSION']]['PORT']
                    )
                )
            if Environment.SERVER['SESSION'] == 'redis':
                import redis
                cls._app.config['SESSION_REDIS'] = redis.from_url("%s://%s:%d/redis" % (
                    Environment.SERVER['SESSION'],
                    Environment.Services[Environment.SERVER['SESSION']]['HOST'],
                    Environment.Services[Environment.SERVER['SESSION']]['PORT']
                )
                                                                  )
            if Environment.SERVER['SESSION'] == 'sqlalchemy':
                from flask_framework.database import Database
                cls._app = Database.setup_sessions(
                    cls._app
                )
            if Environment.SERVER['SESSION'] == 'mongodb':
                from pymongo import MongoClient
                db_conf = Environment.Services[Environment.SERVER['SESSION']]
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
                from flask_login_oidc import FlaskOIDC
                cls.openid = FlaskOIDC(prefix='OpenID')
                cls.openid.init_app(cls._app)
            if 'SAML2' in Environment.Logins:
                from flask_login_saml.client import FlaskSAML
                cls.saml = FlaskSAML(prefix='SAML2')
                cls.saml.init_app(cls._app)
        cls._socket = SocketIO()
        if 'SOCKETIO_ENGINE' in Environment.FLASK['CONFIG']:
            if Environment.FLASK['CONFIG']['SOCKETIO_ENGINE']:
                if 'SOCKETIO_MESSAGE_QUEUE' in Environment.FLASK['CONFIG']:
                    cls._socket.init_app(cls._app, message_queue=Environment.FLASK['CONFIG']['SOCKETIO_MESSAGE_QUEUE'])
                else:
                    cls._socket.init_app(cls._app)
        return cls._app

    @classmethod
    def instantiate(cls):
        """
            :return:
            :rtype: flask.Flask
        """
        cls._scheduler = APScheduler()
        if 'JOBS' not in cls._app.config:
            cls._app.config['JOBS'] = []
        if 'SCHEDULER_API_ENABLED' not in cls._app.config:
            cls._app.config['SCHEDULER_API_ENABLED'] = False
            cls._scheduler.init_app(cls._app)
            cls._scheduler.start()
            # logger.info("Starting listening on " + args.listening_address + " on port " + args.listening_port)
        return cls._app

    @classmethod
    def start(cls, args):
        """
        Start flask application using WSGIServer. This method is blocking and is the main process.
        Can be stopped using keyboard signals
        :param args: needs arguments listening_address (nullable), listening_port (required) and pid (nullable)
        :type args: argparse.Namespace
        :return:
        """
        cls._args = args
        cls._scheduler = APScheduler()
        if 'JOBS' not in cls._app.config:
            cls._app.config['JOBS'] = []
        if 'SCHEDULER_API_ENABLED' not in cls._app.config:
            cls._app.config['SCHEDULER_API_ENABLED'] = False
        if args.listening_address is not None:
            cls._scheduler.init_app(cls._app)
            cls._scheduler.start()
            # logger.info("Starting listening on " + args.listening_address + " on port " + args.listening_port)
            print("Starting listening on %s on port %d" % (args.listening_address, int(args.listening_port)))
            if 'SSL' in Environment.SERVER:
                if args.debug:
                    cls._app.run(
                        host=args.listening_address,
                        port=int(args.listening_port),
                        debug=args.debug,
                        ssl_context=(Environment.SERVER['SSL']['Certificate'], Environment.SERVER['SSL']['PrivateKey']))
                else:
                    try:
                        if args.pid:
                            cls.pid()
                        cls._server = WSGIServer(
                            (args.listening_address, int(args.listening_port)),
                            cls._app,
                            keyfile=Environment.SERVER['SSL']['PrivateKey'],
                            certfile=Environment.SERVER['SSL']['Certificate']
                        )
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
            # logger.info("Starting listening on 0.0.0.0 on port " + args.listening_port)
            print("Starting listening on 0.0.0.0 on port %d" % int(args.listening_port))
            if 'SSL' in Environment.SERVER:
                if args.debug:
                    cls._app.run(
                        host="0.0.0.0",
                        port=int(args.listening_port),
                        debug=args.debug,
                        ssl_context=(Environment.SERVER['SSL']['Certificate'], Environment.SERVER['SSL']['PrivateKey']))
                else:
                    try:
                        if args.pid:
                            cls.pid()
                        cls._server = WSGIServer(
                            ("0.0.0.0", int(args.listening_port)),
                            cls._app,
                            keyfile=Environment.SERVER['SSL']['PrivateKey'],
                            certfile=Environment.SERVER['SSL']['Certificate']
                        )
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
            # logger.info("Server is running")

    @classmethod
    def wsgi_setup(cls):
        """

        :return:
        :rtype: flask.Flask
        """
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
        """
        Part that loads all websocket events in working directory where the framework is called.
        Provides Process._socket attribute to socket as argument.
        """
        if cls._socket is not None:
            socket.Handler(cls._socket)

    @classmethod
    def load_plugins(cls):
        """
        Part that enable plugin to be loaded on working directory where the framework is called.
        Provides
        Process._app, Process._scheduler, Process._session (nullable), Process._csrf (nullable), Process._socket
        attributes to plugins as argument.
        """
        plugins.Load(
            srv=cls._app,
            scheduler=cls._scheduler,
            session=getattr(cls, "_session", None),
            csrf=getattr(cls, "_csrf", None),
            socket=cls._socket
        )

    @classmethod
    def load_routes(cls):
        """
        Part that loads all endpoints / routes in working directory where the framework is called.
        Provides Process._app attribute to routes and request before / after handler as argument.
        """
        handler.Init(cls._app)
        ws.Route(cls._app)
        web.Route(cls._app)
        errors.Route(cls._app)

    @classmethod
    def load_middleware(cls):
        """
        Part that enable middlewares to be loaded on working directory where the framework is called.
        Provides Process._app attribute to plugins as argument.
        """
        middleware.Load(cls._app)

    @classmethod
    def get_ws(cls):
        """

        :return:
        :rtype: flask_socketio.SocketIO
        """
        return cls._socket

    @classmethod
    def add_task(cls, function, id=None, args=(), trigger='interval', seconds=0, minutes=0, hours=0, days=0, weeks=0):
        """
        Adds scheduled functions to flask
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
            cls._app.config['SCHEDULER_JOBSTORES'] = {
                'default': apscheduler.jobstores.redis.RedisJobStore(
                    port=Environment.Services['redis']['PORT'],
                    host=Environment.Services['redis']['HOST'],
                    db=10
                )
            }
            cls._app.config['SCHEDULER_API_ENABLED'] = True

    @classmethod
    def add_cron(cls, function, id=None, args=(), trigger='interval', seconds=0, minutes=0, hours=0, days=0, weeks=0):
        """
        Adds cron functions to flask
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
        if seconds == 0 and minutes == 0 and hours == 0 and days == 0 and weeks == 0:
            seconds = 1
        cls._scheduler.add_job(
            id=id if id is not None else function,
            func=function.replace('.', ':', 1),
            args=args,
            trigger=trigger,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            days=days
        )
        if 'SCHEDULER_API_ENABLED' not in cls._app.config:
            cls._app.config['SCHEDULER_API_ENABLED'] = True

    @classmethod
    def add_parallel_task(cls, function, id=None, args=(), trigger='date', date=datetime.now() + timedelta(0, 0)):
        """
        Adds functions to be executed in parallel to flask
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
        cls._scheduler.add_job(
            id=function,
            func=function.replace('.', ':', 1),
            args=args,
            trigger=trigger,
            run_date=date
        )
        cls._scheduler.run_job(id=id if id is not None else function)
        if 'SCHEDULER_API_ENABLED' not in cls._app.config:
            cls._app.config['SCHEDULER_API_ENABLED'] = True

    @classmethod
    def pid(cls):
        """
        Creates a pid file for the current process.
        """
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
        Removes the pid file.
        """
        os.unlink(cls._pidfile)

    @classmethod
    def get(cls):
        """
        Returns the current running fastapi instance
        :return:
        :rtype: flask.Flask
        """
        return cls._app

    @classmethod
    def stop(cls, code=0):
        """
        Shutdown the current process.
        :param code:
        :type: int
        :return:
        """
        if cls._args.pid:
            cls.shutdown()
        exit(code)

    @classmethod
    def init_sheduler(cls):
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

    @classmethod
    def login_manager(cls, login_manager=None):
        """
        Use to set up or retrieve user login manager rules on flask, needs flask_login installed
        :param login_manager:
        :type login_manager: flask_login.LoginManager
        :return:
        :rtype: flask_login.LoginManager
        """
        if login_manager:
            try:
                from flask_login import LoginManager
                if (
                        not callable(login_manager)
                        and isinstance(login_manager, object)
                        and type(login_manager) is LoginManager
                ):
                    cls._login_manager = login_manager
            except ImportError:
                pass
        return cls._login_manager



    @classmethod
    def csrf(cls, csrf=None):
        """
        Return CSRFProtect instance if it API_KEY has been within configuration otherwise can be set later
        on plugins loading step
        :param csrf:
        :type csrf: flask_wtf.CSRFProtect
        :return:
        :rtype: flask_wtf.CSRFProtect | None
        """
        if csrf:
            try:
                from flask_wtf import CSRFProtect
                if (
                        not callable(csrf)
                        and isinstance(csrf, object)
                        and type(csrf) is CSRFProtect
                ):
                    cls._csrf = csrf
            except ImportError:
                pass
        return cls._csrf
