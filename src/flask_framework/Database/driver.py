# coding: utf-8


__author__ = 'Frederick NEY'

import logging
import sqlalchemy.orm.query

try:
    import pandas
except ImportError:
    pass

from sqlalchemy import create_engine, Engine
from sqlalchemy.dialects import registry
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from flask_framework.Config import Environment
from flask_framework.Deprecation import deprecated, outdated, Future


class Driver(object):
    engine: Engine = None
    session: scoped_session = None
    Model: registry = None
    _sessionmaker: sessionmaker = None
    Managers = []
    engines: dict = {}
    sessions: dict = {}
    models: dict = {}
    _sessionmakers: dict = {}

    @staticmethod
    def _params(args={}, separator=';'):
        array_args = list(args.items())
        params = str()
        for i in range(0, len(array_args)):
            params += \
                '{}={}{}'.format(array_args[i][0], array_args[i][1], separator) if i < len(array_args) - 1 else \
                    '{}={}'.format(array_args[i][0], array_args[i][1])
        return params

    @classmethod
    def setup(
            cls,
            driver, user, pwd, host, db, port=None, echo=False, params=None, dialects=None, **kwargs
    ):
        """
        Setup function that will configure all the required resources for communicating with the database
        :param driver: Database driver that will be used when the server need to store persistent data
        :param user: Database user
        :param pwd: Database password
        :param host: Database host
        :param db: Database schema
        :param echo: Boolean for printing sql request default: false
        :return: N/A
        """
        if dialects is not None:
            for name, values in dialects.items():
                registry.register(name, values['module'], values['class'])
        _url_param_separator = '?' if kwargs is None else kwargs.pop('url_param_separator', '?')
        _params_separator = '&' if kwargs is None else kwargs.pop('params_separator', '&')
        database_uri = (
                "{}://{}:{}@{}:{}/{}".format(driver, user, pwd, host, port, db)
                + ('{}{}'.format(_url_param_separator, cls._params(params, _params_separator)) if params is not None else '')
        ) if port else (
                "{}://{}:{}@{}/{}".format(driver, user, pwd, host, db)
                + ('{}{}'.format(_url_param_separator, cls._params(params, _params_separator)) if params is not None else '')
        )
        cls.engine = create_engine(database_uri, echo=echo, **kwargs)
        cls._sessionmaker = sessionmaker(bind=cls.engine, autoflush=True)
        cls.session = scoped_session(cls._sessionmaker)
        cls.Model = declarative_base()
        cls.Model.query = cls.session.query_property()

    @classmethod
    def register_engine(
            cls,
            name, driver, user, pwd, host, db, port=None, params=None, dialects=None, echo=True, **kwargs
    ):
        if dialects is not None:
            for registry_name, values in dialects.items():
                registry.register(registry_name, values['module'], values['class'])
        _url_param_separator = '?' if kwargs is None else kwargs.pop('url_param_separator', '?')
        _params_separator = '&' if kwargs is None else kwargs.pop('params_separator', '&')
        database_uri = (
                "{}://{}:{}@{}:{}/{}".format(driver, user, pwd, host, port, db)
                + ('{}{}'.format(_url_param_separator, cls._params(params, _params_separator)) if params is not None else '')
        ) if port else (
                "{}://{}:{}@{}/{}".format(driver, user, pwd, host, db)
                + ('{}{}'.format(_url_param_separator, cls._params(params, _params_separator)) if params is not None else '')
        )
        cls.engines[name] = create_engine(database_uri, echo=echo, **kwargs)
        cls._sessionmakers[name] = sessionmaker(bind=cls.engines[name], autoflush=False)
        cls.sessions[name] = scoped_session(cls._sessionmakers[name])
        cls.models[name] = declarative_base()
        cls.models[name].query = cls.sessions[name].query_property()

    @classmethod
    def get_session_by_name(cls, name):
        if name in cls.sessions:
            return cls.sessions[name]
        return None

    @classmethod
    def start_session_by_name(cls, name):
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
            logging.info("{}: setting database {}".format(__name__, driver))
            engines_params = {}
            if 'engine' in config:
                engines_params.update(config['engine'])
            cls.register_engine(
                driver,
                config['driver'],
                config['user'],
                config['password'],
                config['address'],
                config['database'],
                port=(config['port'] if 'port' in config else None),
                params=(config['params'] if 'params' in config else None),
                dialects=(config['dialects'] if 'dialects' in config else None),
                echo=echo,
                **engines_params
            )
            if driver == "default":
                cls.setup(
                    config['driver'],
                    config['user'],
                    config['password'],
                    config['address'],
                    config['database'],
                    port=(config['port'] if 'port' in config else None),
                    params=(config['params'] if 'params' in config else None),
                    dialects=(config['dialects'] if 'dialects' in config else None),
                    echo=echo,
                    **engines_params
                )

    @classmethod
    @Future.remove
    def start_sessions(cls):
        for driver, config in Environment.Databases.items():
            cls.start_session(driver)
            if driver == 'default':
                cls.start_default_session()

    @classmethod
    @Future.remove
    def start_session(cls, name):
        cls.sessions[name] = scoped_session(cls._sessionmakers[name])

    @classmethod
    @Future.remove
    def start_default_session(cls):
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
    @outdated
    def add_task_db_session(cls, task_name, db='default'):
        pass

    @classmethod
    @outdated
    def get_task_session(cls, task_name):
        pass

    @classmethod
    def init_default_db(cls):
        try:
            import models.persistent
        except ImportError as e:
            logging.debug("{}: {}".format(__name__, e))
            try:
                import Models.Persistent
            except ImportError as e:
                logging.debug("{}: {}".format(__name__, e))
        logging.info("{}: creating models for default database".format(
            __name__
        ))
        cls.Model.metadata.create_all(bind=cls.engine)

    @classmethod
    def init_db(cls, name):
        try:
            import models.persistent
        except ImportError as e:
            logging.debug("{}: {}".format(__name__, e))
            try:
                import Models.Persistent
            except ImportError as e:
                logging.debug("{}: {}".format(__name__, e))
        logging.info("{}: creating models for {} database".format(
            __name__,
            name
        ))
        cls.models[name].metadata.create_all(bind=cls.engines[name])

    @classmethod
    def init(cls):
        """
        Function that create schema tables based on imported models within this function
        :return: N/A
        """
        for driver, conf in Environment.Databases.items():
            logging.info("{}: looking for models into {} for database {}".format(
                __name__,
                conf['models'],
                driver)
            )
            if driver == 'default':
                if not conf['readonly']:
                    cls.init_default_db()
            elif not conf['readonly']:
                cls.init_db(name=driver)

    @classmethod
    def disconnect(cls, engine, session):
        session.close()
        engine.dispose()

    @classmethod
    def disconnect_all(cls):
        for name, engine in cls.engines.items():
            cls.disconnect(engine, cls.sessions[name])
        cls.disconnect(cls.engine, cls.session)

    @classmethod
    def reconnect_all(cls):
        cls.disconnect_all()
        cls.register_engines()

    @classmethod
    @outdated
    def save(cls):
        pass

    @staticmethod
    @outdated
    def update():
        pass

    @staticmethod
    @deprecated('Use close_sessions')
    def shutdown_session(exception=None):
        """
        Function that means to be used for ending database session before the server will be shut down
        :param exception:
        :return: N/A
        """
        Driver.close_sessions()
    
    @classmethod
    def to_pandas(cls, query: sqlalchemy.orm.query.Query, engine: str = None):
        """
        Convert SQLAlchemy query object into pandas Dataframe
        Experimental use at your own risk.
        :param query: SQLAlchemy query
        :type query: sqlalchemy.orm.query.Query
        :param engine: Database connection to use
        :type engine: str | None
        :return:
        :rtype: pandas.DataFrame | None
        """
        try:
            if engine is None:
                return pandas.read_sql(
                    str(query.statement.compile(compile_kwargs={"literal_binds": True})),
                    cls.engine
                )
            else:
                return pandas.read_sql(
                    str(query.statement.compile(compile_kwargs={"literal_binds": True})),
                    cls.engines[engine]
                )
        except NameError as e:
            logging.error("{}: pandas not installed as {}".format(__name__, e))
        return None
