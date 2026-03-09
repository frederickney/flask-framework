# coding: utf-8


__author__ = 'Frederick NEY'

import logging
import typing
import sqlalchemy.orm.query
import sqlalchemy.sql.selectable

try:
    import pandas
except ImportError:
    pass

try:
    import pandas
except ImportError:
    pass
try:
    from sqlalchemy import create_engine, Engine
except ImportError:
    from sqlalchemy import create_engine
    from sqlalchemy.engine import Engine
from sqlalchemy.dialects import registry
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from flask_framework.Config import Environment

from flask_framework.Deprecation import  outdated, Future


class Driver(object):
    """
    Class Driver act as a singleton where after loaded all
    the content of the attributes is available at any part of the project.

    Requires fastapi_flask_framework.Config.Environment to be loaded first.

    >>> import os
    >>> Environment.load(os.environ['CONFIG_FILE'])
    >>> Driver.register_engines()
    >>> Driver.init()

    Contains following attributes:
    Attributes
    ----------

    engine: sqlalchemy.engine.Engine
        Defaut database engine, usable if default is set within:

        >>> Environment.Databases
    session: sqlalchemy.orm.session.Session
        Default database session, usable if default is set within:

        >>> Environment.Databases
    Model:
        Default database Model class, usable if default is set within:

        >>> Environment.Databases
    engines: dict[str, sqlalchemy.engine.Engine]
        registered database engines. Contains all keys from:

        >>> Environment.Databases
    sessions: dict[str, sqlalchemy.orm.session.Session]
        registered database sessions. Contains all keys from:

        >>> Environment.Databases
    models: dict[str, sqlalchemy.orm.declarative.DeclarativeBase]
        registered database models. Contains all keys from:

        >>> Environment.Databases
    """
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
        """
        Prepares database parameters that is set within database's connection url
        :param args:
        :type args: dict[str, str|int|bool]
        :param separator:
        :type separator: str
        :return: url formated parameters
        :rtype: str
        """
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
        Setup function that will configure all the required resources for communicating with the default database
        :param driver: Database driver that will be used when the server need to store persistent data
        :type driver: str
        :param user: Database user
        :type user: str | None
        :param pwd: Database password
        :type pwd: str | None
        :param host: Database host
        :type host: str
        :param db: Database schema
        :type db: str
        :param port: Database port
        :type port: int | None
        :param params: Database parameters
        :type params: dict[str, str | int | bool]
        :param dialects: Database dialects
        :type dialects: dict[str, Any]
        :param echo: Boolean for printing sql request default: false
        :type echo: bool
        :param kwargs: sqlalchemy.create_engine keyword arguments
        :type kwargs: dict[str, Any]
        """
        if dialects is not None:
            for name, values in dialects.items():
                registry.register(name, values['module'], values['class'])
        # Determining the escape character before parameters and after database url
        _url_param_separator = '?' if kwargs is None else kwargs.pop('url_param_separator', '?')
        # Determining the escape character in between parameters
        _params_separator = '&' if kwargs is None else kwargs.pop('params_separator', '&')
        # Setting up sqlalchemy database url connection
        database_uri = (
                "{}://{}{}:{}/{}".format(driver, "{}:{}@".format(user, pwd) if user is not None else "", host, port, db)
                + ('{}{}'.format(_url_param_separator, cls._params(params, _params_separator)) if params is not None else '')
        ) if port else (
                "{}://{}{}/{}".format(driver, "{}:{}@".format(user, pwd) if user is not None else "", host, db)
                + ('{}{}'.format(_url_param_separator, cls._params(params, _params_separator)) if params is not None else '')
        )
        # creates database connection
        cls.engine = create_engine(database_uri, echo=echo, **kwargs)
        # prepares database session
        cls._sessionmaker = sessionmaker(bind=cls.engine, autoflush=True)
        # creates database session
        cls.session = scoped_session(cls._sessionmaker)
        # creates Model base object
        cls.Model = declarative_base()
        cls.Model.query = cls.session.query_property()

    @classmethod
    def register_engine(
            cls,
            name, driver, user, pwd, host, db, port=None, params=None, dialects=None, echo=True, **kwargs
    ):
        """
        Setup function that will configure all the required resources for communicating with the database.
        :param name: Database configuration name
        :type name: str
        :param driver: Database driver that will be used when the server need to store persistent data
        :type driver: str
        :param user: Database user
        :type user: str | None
        :param pwd: Database password
        :type pwd: str | None
        :param host: Database host
        :type host: str
        :param db: Database schema
        :type db: str
        :param port: Database port
        :type port: int | None
        :param params: Database parameters
        :type params: dict[str, str | int | bool]
        :param dialects: Database dialects
        :type dialects: dict[str, Any]
        :param echo: Boolean for printing sql request default: false
        :type echo: bool
        :param kwargs: sqlalchemy.create_engine keyword arguments
        :type kwargs: dict[str, Any]
        """
        if dialects is not None:
            for registry_name, values in dialects.items():
                registry.register(registry_name, values['module'], values['class'])
        # Determining the escape character before parameters and after database url
        _url_param_separator = '?' if kwargs is None else kwargs.pop('url_param_separator', '?')
        # Determining the escape character in between parameters
        _params_separator = '&' if kwargs is None else kwargs.pop('params_separator', '&')
        # Setting up sqlalchemy database url connection
        database_uri = (
                "{}://{}{}:{}/{}".format(driver, "{}:{}@".format(user, pwd) if user is not None else "", host, port, db)
                + ('{}{}'.format(_url_param_separator, cls._params(params, _params_separator)) if params is not None else '')
        ) if port else (
                "{}://{}{}/{}".format(driver, "{}:{}@".format(user, pwd) if user is not None else "", host, db)
                + ('{}{}'.format(_url_param_separator, cls._params(params, _params_separator)) if params is not None else '')
        )
        # creates database connection
        cls.engines[name] = create_engine(database_uri, echo=echo, **kwargs)
        # prepares database session
        cls._sessionmakers[name] = sessionmaker(bind=cls.engines[name], autoflush=False)
        # creates database session
        cls.sessions[name] = scoped_session(cls._sessionmakers[name])
        # creates Model base object
        cls.models[name] = declarative_base()
        cls.models[name].query = cls.sessions[name].query_property()

    @classmethod
    @Future.replace(version='1.3.0', name='flask_framework.database.Driver methods')
    def get_session_by_name(cls, name):
        """
        Get a session by name
        :param name: Database configuration name
        :type name: str
        :return: Session
        :rtype: sqlalchemy.orm.session.Session
        """
        if name in cls.sessions:
            return cls.sessions[name]
        return None

    @classmethod
    @Future.replace(version='1.3.0', name='flask_framework.database.Driver methods')
    def start_session_by_name(cls, name):
        return scoped_session(cls._sessionmakers[name])

    @classmethod
    @Future.replace(version='1.3.0', name='flask_framework.database.Driver methods')
    def get_engine_by_name(cls, name):
        """
        Get sqlalchemy engine by name
        :param name: Database configuration name
        :type name: str
        :return: Engine
        :rtype: sqlalchemy.engine.Engine
        """
        if name in cls.engines:
            return cls.engines[name]
        return None

    @classmethod
    @Future.replace(version='1.3.0', name='flask_framework.database.Driver methods')
    def get_model_by_name(cls, name):
        """
        Get sqlalchemy model by name
        :param name: Database configuration name
        :type name: str
        :return: sqlalchemy.orm.declarative.DeclarativeBase
        """
        if name in cls.models:
            return cls.models[name]
        return None

    @classmethod
    @Future.replace(version='1.3.0', name='flask_framework.database.Driver methods')
    def register_engines(cls, echo=False):
        """
        Register databases engines
        """
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
    @Future.replace(version='1.3.0', name='flask_framework.database.Driver methods')
    def close_sessions(cls):
        for driver, config in Environment.Databases.items():
            cls.close_session(driver)
            if driver == 'default':
                cls.close_default_session()

    @classmethod
    @Future.replace(version='1.3.0', name='flask_framework.database.Driver methods')
    def close_session(cls, name):
        """
        Close a database session by name
        """
        cls.sessions[name].close()

    @classmethod
    @Future.replace(version='1.3.0', name='flask_framework.database.Driver methods')
    def close_default_session(cls):
        """
        Close default database session
        """
        cls.session.close()

    @classmethod
    @outdated
    def setup_sessions(cls, app):
        """
        :return:
        :rtype: flask.Flask
        """
        app.config["SESSION_SQLALCHEMY_TABLE"] = 'sessions'
        app.config["SESSION_SQLALCHEMY"] = cls.engine
        return app

    @classmethod
    def init_default_db(cls):
        """
        Initialize default database models and registers models stored onto module
        models.persistent
        """
        try:
            # needs to be loaded after the database registration otherwise will raise NameError exception
            import models.persistent
        except ImportError as e:
            logging.debug("{}: {}".format(__name__, e))
            try:
                # needs to be loaded after the database registration otherwise will raise NameError exception
                import Models.Persistent
            except ImportError as e:
                logging.debug("{}: {}".format(__name__, e))
        logging.info("{}: creating models for default database".format(
            __name__
        ))
        cls.Model.metadata.create_all(bind=cls.engine)

    @classmethod
    def init_db(cls, name):
        """
        Initialize database models and registers models stored onto module
        models.persistent
        """
        try:
            # needs to be loaded after the database registration otherwise will raise NameError exception
            import models.persistent
        except ImportError as e:
            logging.debug("{}: {}".format(__name__, e))
            try:
                # needs to be loaded after the database registration otherwise will raise NameError exception
                import Models.Persistent
            except ImportError as e:
                logging.debug("{}: {}".format(__name__, e))
        logging.info("{}: creating models for {} database".format(
            __name__,
            name
        ))
        cls.models[name].metadata.create_all(bind=cls.engines[name])

    @classmethod
    @Future.replace(version='1.3.0', name='flask_framework.database.Driver methods')
    def init(cls):
        """
        Function that create schema tables based on imported models within this function.
        needs to be called after Driver.register_engines()
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
    @Future.replace(version='1.3.0', name='flask_framework.database.Driver methods')
    def disconnect(cls, engine, session):
        """
        Function that disconnect safely database
        """
        session.close()
        engine.dispose()

    @classmethod
    @Future.replace(version='1.3.0', name='flask_framework.database.Driver methods')
    def disconnect_all(cls):
        """
        Function that disconnect safely all databases
        """
        for name, engine in cls.engines.items():
            cls.disconnect(engine, cls.sessions[name])
        cls.disconnect(cls.engine, cls.session)

    @classmethod
    @Future.replace(version='1.3.0', name='flask_framework.database.Driver methods')
    def reconnect_all(cls):
        """
        Function that reconnect safely all databases by disconnecting them and reconnecting them
        """
        cls.disconnect_all()
        cls.register_engines()

    @classmethod
    @Future.replace(version='1.3.0', name='flask_framework.database.Driver methods')
    def to_pandas(cls, query: typing.Union[sqlalchemy.orm.query.Query, sqlalchemy.sql.selectable.Select], engine: str = None):
        """
        Convert SQLAlchemy query object into pandas Dataframe
        Experimental use at your own risk.
        :param query: SQLAlchemy query or select
        :type query: sqlalchemy.orm.query.Query | sqlalchemy.sql.selectable.Select
        :param engine: Database connection to use
        :type engine: str | None
        :return:
        :rtype: pandas.DataFrame | None
        """
        try:
            if engine is None:
                return pandas.read_sql(
                    str(query.statement.compile(compile_kwargs={"literal_binds": True})) if type(query) is
                        sqlalchemy.orm.query.Query else
                    str(query.compile(compile_kwargs={"literal_binds": True})),
                    cls.engine
                )
            else:
                return pandas.read_sql(
                    str(query.statement.compile(compile_kwargs={"literal_binds": True})) if type(query) is
                        sqlalchemy.orm.query.Query else
                    str(query.compile(compile_kwargs={"literal_binds": True})),
                    cls.engines[engine]
                )
        except NameError as e:
            logging.error("{}: pandas not installed as {}".format(__name__, e))
        return None
