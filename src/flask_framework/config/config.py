# coding: utf-8


__author__ = 'Frederick NEY'

import logging

from flask_framework import exceptions
from flask_framework.exceptions.runtime import web_denied
from . import yaml


def _load(file, loader):
    """
    Load file for the framework's configuration
    :param file: path to file to load
    :type file: str
    :param loader: file handler that has a load method in it
    :type loader: yaml
    :return: loaded file in the format the loader returns
    :rtype: any
    """
    return loader.load(file)


def load_file(file, loader=yaml):
    """
    Load
    :param file: path to file to load
    :type file: str
    :param loader: (Optional default: yaml) File handler that has a load method in it
    :type loader: yaml
    :return: loaded file in the format the loader returns
    :rtype: any
    """
    conf = _load(file, loader)
    return conf


class Environment(object):
    """
    Class Environment act as a singleton where after loaded all
    the content of the attributes is available at any part of the project.

    Requires CONFIG_FILE environment variable to be set before loading.

    Needs to be loaded first with:

    >>> import os
    >>> Environment.load(os.environ['CONFIG_FILE'])

    Contains following attributes:
    Attributes
    ----------

    SERVER:
        It uses the SERVER field within the yaml configuration file.
    FLASK:
        Setup conf for Flask.
        It uses the Flask field within the yaml configuration file.
    Databases:
        All databases related configuration for sqlalchemy database engines.
        It uses the DATABASES field within the yaml configuration file.
    Logins:
        All logins method related configuration for user authentications.
        It uses the LOGINS field within the yaml configuration file.
    Services:
        All other configuration setup.
        It uses the SERVICES field within the yaml configuration file.
    """
    SERVER = {}
    Databases = {}
    Logins = {}
    Services = {}
    FLASK = {}
    __default_runtime_change = False

    @staticmethod
    def _load(file, loader):
        """
        Load config file using a specific file handler
        :param file: path to file to load
        :type file: str
        :param loader:
        :type loader: yaml
        """
        return loader.load(file)

    @classmethod
    @web_denied
    def reload(cls, file):
        """
        Triggered on uvicorn reload or flask reload on debug
        :param file: path to file to load
        :type file: str
        """
        from . import yaml
        conf = cls._load(file, yaml)
        cls.load_runtime(conf)
        cls.load_logins(conf)
        cls.load_services(conf)
        cls.FLASK = conf['FLASK'] if 'FLASK' in conf else cls.FLASK

    @classmethod
    @web_denied
    def load(cls, file):
        """
        Load configuration file. and fulfills class's attributes for handling them anywhere on the code.
        :param file: path to file to load
        """
        conf = cls._load(file, yaml)
        cls.load_runtime(conf)
        cls.load_databases(conf)
        cls.load_logins(conf)
        cls.load_services(conf)
        cls.FLASK = conf['FLASK'] if 'FLASK' in conf else cls.FLASK
        cls.FLASK.setdefault('CONFIG', {})

    @classmethod
    @web_denied
    def load_databases(cls, conf):
        """
        Load database configurations into Databases class's attribute
        :param conf: dictionary with all the content of the config file
        :type conf: dict[str, dict]
        """
        try:
            for type in conf["DATABASES"]:
                if type != 'default':
                    cls.add_database(type, conf["DATABASES"][type])
                else:
                    cls.set_default_database(conf["DATABASES"][conf["DATABASES"][type]])
        except KeyError:
            cls.Databases = {}

    @classmethod
    def add_database(cls, db_type, db_conf):
        """
        Add database configuration within Databases class's attribute
        :param db_type: database type
        :type db_type: str
        :param db_conf: database configuration
        :type db_conf: dict[str, dict|str|int]
        :raises flask_framework.Exceptions.RuntimeExceptions.DatabaseChangeException:
        if the database is already loaded within Databases class's attribute
        """
        db = cls.Databases.get(db_type, None)
        if db is None:
            cls.Databases[db_type] = db_conf
        elif db is not None:
            logging.warning("Database '{}' already set".format(db_type))
            raise exceptions.runtime.DatabaseChangeException(
                "Not permitted to change database '{}'  while app is running".format(db_type)
            )

    @classmethod
    @web_denied
    def set_default_database(cls, db_conf):
        """
        Add default database configuration within Databases class's attribute
        :param db_type: database type
        :type db_type: str
        :param db_conf: database configuration
        :type db_conf: dict[str, dict|str|int]
        :raises flask_framework.Exceptions.RuntimeExceptions.DatabaseChangeException:
        if the default database is already loaded within Databases class's attribute
        """
        db = cls.Databases.get('default', None)
        if db is None and cls.__default_runtime_change is False:
            cls.Databases['default'] = db_conf
            cls.__default_runtime_change = True
        elif db is not None:
            logging.warning("Default database already set")
        else:
            raise exceptions.runtime.DatabaseChangeException(
                "Not permitted to change default database while app is running"
            )

    @classmethod
    @web_denied
    def load_logins(cls, conf):
        """
        Load logins configurations into Logins class's attribute
        :param conf: dictionary with all the content of the config file
        :type conf: dict[str, dict]
        """
        cls.Logins = conf['LOGINS'] if 'LOGINS' in conf else cls.Logins

    @classmethod
    def add_login(cls, login_name, login_conf):
        """
        Add logins configurations into Logins class's attribute
        :param login_name: Login identifier
        :type login_name: str
        :param login_conf: login configuration
        :type login_conf: dict[str, dict|str|int]
        """
        login = cls.Logins.get(login_name, None)
        if login is None:
            cls.Logins[login_name] = login_conf
        elif login is not None:
            logging.warning("Login service '{}' already set".format(login_name))
            raise exceptions.runtime.LoginChangeException(
                "Not permitted to change login method '{}'  while app is running".format(login_name)
            )

    @classmethod
    @web_denied
    def load_runtime(cls, conf):
        """
        Load deployment setup configurations into SERVER class's attribute
        :param conf: dictionary with all the content of the config file
        :type conf: dict[str, dict]
        """
        cls.SERVER = conf['SERVER']

    @classmethod
    @web_denied
    def load_services(cls, conf):
        """
        Load other attributes configurations into Services class's attribute
        :param conf: dictionary with all the content of the config file
        :type conf: dict[str, dict]
        """
        cls.Services.update(conf['SERVICES'] if 'SERVICES' in conf else cls.Services)

    @classmethod
    def add_service(cls, service_name, service_conf):
        """
        Add other attributes configurations into Services class's attribute
        :param service_name: service identifier
        :type service_name: str
        :param service_conf: service configuration
        :type service_conf: dict[str, dict|str|int]
        """
        service = cls.Services.get(service_name, None)
        if service is None:
            cls.Services[service_name] = service_conf
        elif service is not None:
            logging.warning("Service '{}' changed".format(service_name))
            cls.Services[service_name] = service_conf
