# coding: utf-8

__author__ = 'Frederick NEY'

from flask_sqlalchemy import BaseQuery, Lock, Model

from Config import Environment
from Deprecation import deprecated


class SQLAlchemy(object):

    def __init__(self, app=None, use_native_unicode=True,query=BaseQuery,session=None, model=Model, engine=None):
        import sqlalchemy, sqlalchemy.orm
        self.use_native_unicode = use_native_unicode
        self.Query = query
        self.engine = engine
        self.session = session
        self.Model = model
        self._engine_lock = Lock()
        self.app = app
        for module in sqlalchemy, sqlalchemy.orm:
            for key in module.__all__:
                if not hasattr(self, key):
                    setattr(self, key, getattr(module, key))
            # Note: obj.Table does not attempt to be a SQLAlchemy Table class.
    @property
    def metadata(self):
        return self.Model.metadata

class Driver(object):

    engine = None
    session = None
    Model = None
    _sessionmaker = None
    Managers = []
    engines = {}
    sessions = {}
    models = {}
    _sessionmakers = {}
    _sqlalchemy = None
    _sqlalchemy_array = {}

    @staticmethod
    def _params(args={}):
        array_args = list(args.items())
        params = str()
        for i in range(0, len(array_args)):
            params += \
                '{}={};'.format(array_args[i][0], array_args[i][1]) if i < len(array_args) - 1 else \
                '{}={}'.format(array_args[i][0], array_args[i][1])
        return params

    @classmethod
    def setup(cls, driver, user, pwd, host, db, echo=False, params=None, dialects=None, **kwargs):
        """
        Setup function that will configure all the required resources for communicating with the database
        :param driver: Database driver that will be used when the server need to store persistant data
        :param user: Database user
        :param pwd: Database password
        :param host: Database host
        :param db: Database schema
        :param echo: Boolean for printing sql request default: false
        :return: N/A
        """
        from sqlalchemy import create_engine
        from sqlalchemy.orm import scoped_session, sessionmaker
        from sqlalchemy.ext.declarative import declarative_base
        if dialects is not None:
            from sqlalchemy.dialects import registry
            for name, values in dialects.items():
                registry.register(name, values['module'], values['class'])
        database_uri =  "{}://{}:{}@{}/{}".format(driver, user, pwd, host, db) \
                        + ('?{}'.format(cls._params(params)) if params is not None else '')
        cls.engine = create_engine(database_uri, echo=echo)
        cls._sessionmaker = sessionmaker(bind=cls.engine)
        cls.session = scoped_session(cls._sessionmaker)
        cls.Model = declarative_base(cls.session)
        cls.Model.query = cls.session.query_property()
        cls._sqlalchemy = SQLAlchemy(engine=cls.engine, query=cls.session.query_property(), session=cls.session, model=cls.Model)
        cls.session.close()


    @classmethod
    def register_engine(cls, name, driver, user, pwd, host, db, params=None, dialects=None,  echo=False):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import scoped_session, sessionmaker
        from sqlalchemy.ext.declarative import declarative_base
        if dialects is not None:
            from sqlalchemy.dialects import registry
            for registry_name, values in dialects.items():
                registry.register(registry_name, values['module'], values['class'])
        database_uri = "{}://{}:{}@{}/{}".format(driver, user, pwd, host, db) \
                       + (';{}'.format(cls._params(params)) if params is not None else '')
        cls.engines[name] = create_engine(database_uri, echo=echo)
        cls._sessionmakers[name] = sessionmaker(bind=cls.engines[name])
        cls.sessions[name] = scoped_session(cls._sessionmakers[name])
        cls.models[name] = declarative_base(cls.sessions[name])
        cls.models[name].query = cls.sessions[name].query_property()
        cls._sqlalchemy_array[name] = SQLAlchemy(engine=cls.engines[name], query=cls.sessions[name].query_property(), session=cls.sessions[name], model=cls.models[name])
        cls.sessions[name].close()

    @classmethod
    def get_session_by_name(cls, name):
        if name in cls.sessions:
            return cls.sessions[name]
        return None

    @classmethod
    def start_session_by_name(cls, name):
        from sqlalchemy.orm import scoped_session
        return scoped_session(cls._sessionmakers[name])

    @classmethod
    def get_engine_by_name(cls, name):
        if name in cls.engines:
            return cls.engines[name]
        return None

    @classmethod
    def get_model_by_name(cls, name):
        if name in cls.models:
            return cls.models[name]
        return None

    @classmethod
    def register_engines(cls, echo=False):
        for driver, config in Environment.Databases.items():
            cls.register_engine(
                driver,
                config['driver'],
                config['user'],
                config['password'],
                config['address'],
                config['database'],
                params=(config['params'] if 'params' in config else None),
                dialects=(config['dialects'] if 'dialects' in config else None),
                echo=echo
            )
            if driver == "default":
                cls.setup(
                    config['driver'],
                    config['user'],
                    config['password'],
                    config['address'],
                    config['database'],
                    params=(config['params'] if 'params' in config else None),
                    dialects=(config['dialects'] if 'dialects' in config else None),
                    echo=echo
                )

    @classmethod
    def start_sessions(cls):
        for driver, config in Environment.Databases.items():
            cls.start_session(driver)
            if driver == 'default':
                cls.start_default_session()

    @classmethod
    def start_session(cls, name):
        from sqlalchemy.orm import scoped_session
        cls.sessions[name] = scoped_session(cls._sessionmakers[name])
    
    @classmethod
    def start_default_session(cls):
        from sqlalchemy.orm import scoped_session
        cls.session = scoped_session(cls._sessionmaker)

    @classmethod
    def close_sessions(cls):
        for driver, config in Environment.Databases.items():
            cls.close_session(driver)
            if driver == 'default':
                cls.close_default_session()

    @classmethod
    def close_session(cls, name):
        cls.sessions[name].close()

    @classmethod
    def close_default_session(cls): 
        cls.session.close()

    @classmethod
    def setup_sessions(cls, app):
        """
        :return:
        :rtype: flask.Flask
        """
        app.config["SESSION_SQLALCHEMY_TABLE"] = 'sessions'
        app.config["SESSION_SQLALCHEMY"] = cls.engine
        return app

    @classmethod
    def add_task_db_session(cls, task_name, db='default'):
        """
        Function that setup a different session for scheduling task
        :param task_name: The name of the task
        :return:
        """
        from sqlalchemy.orm import scoped_session, sessionmaker
        if db == 'default':
            session = scoped_session(cls._sessionmaker)
            setattr(Driver, task_name, session)
        else:
            session = scoped_session(cls._sessionmakers[db])
            setattr(Driver, task_name, session)

    @classmethod
    def get_task_session(cls, task_name):
        return getattr(Driver, task_name, None)

    @classmethod
    def init_db(cls, name, models):
        import importlib
        importlib.import_module('Models.Persistent.%s' % models)
        cls.engines[name].metadata = cls.models[name].metadata
        cls.models[name].metadata.create_all(bind=cls.engines[name])

    @classmethod
    def init(cls):
        """
        Function that create schema tables based on imported models within this function
        :return: N/A
        """
        for driver, conf in Environment.Databases.items():
            if driver == 'default':
                if not conf['readonly']:
                    import importlib
                    cls.engine.metadata=cls.Model.metadata
                    importlib.import_module('Models.Persistent.%s' % conf['models'])
                    cls.Model.metadata.create_all(bind=cls.engine)
            else:
                if not conf['readonly']:
                    cls.init_db(name=driver, models=conf['models'])




    @classmethod
    def save(cls):
        pass

    @staticmethod
    def update():
        Driver.session.remove()

    @staticmethod
    @deprecated
    def shutdown_session(exception=None):
        """
        Function that means to be used for ending database session before the server will be shut down
        :param exception:
        :return: N/A
        """
        import logging
        logging.info("Shutting down server...")
        for manager in Driver.Managers:
            manager.teardown = True
            manager.join(10)
            if manager.is_alive():
                logging.warning("Unable to properly stop thread '%s'" % manager.getName())
        Driver.session.remove()
        logging.info("Server is now shut down...")
