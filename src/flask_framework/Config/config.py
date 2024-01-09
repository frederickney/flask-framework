# coding: utf-8


__author__ = 'Frederick NEY'


import logging
from flask_framework import Exceptions


def _load_yaml_file():
    return


def load_file(file):
    import os.path, json
    if isinstance(file, str):
        if os.path.exists(file):
            if os.path.isfile(file):
                try:
                    content = open(file, 'r')
                    return content.read()
                except Exception:
                    raise Exceptions.ConfigExceptions.InvalidConfigurationFileError(file + ": File did not exist.")
            else:
                raise Exceptions.ConfigExceptions.NotAConfigurationFileError(file + ": Not a valid file.")
        else:
            raise Exceptions.ConfigExceptions.NotAConfigurationFileError(file + ": File did not exist.")
    else:
        raise Exceptions.ConfigExceptions.NotAConfigurationFileError(
            "Expected " + type(str) + ", got " + type(file) + "."
        )


class Services(object):

    def __init__(self, name, registry):
        self.name = name,
        self.registry = registry


class Environment(object):

    Databases = {}
    SERVER_DATA = {}
    Logins = {}
    Services = {}
    __services_loaded = False
    __srv_runtime = False
    __default_runtime_change = False
    __runtime_change = False
    __login_change = False
    __default_login_change = False

    @staticmethod
    def _load(file, loader):
        return loader.load(file)

    @classmethod
    def load(cls, file):
        try:
            from . import json
            conf = cls._load(file, json)
        except Exceptions.ConfigExceptions.InvalidConfigurationFileError as e:
            logging.info(e.message)
            from . import yaml
            conf = cls._load(file, yaml)
        cls.load_runtime(conf)
        cls.load_databases(conf)
        cls.load_logins(conf)
        cls.load_services(conf)
        cls.FLASK = conf['FLASK']

    @classmethod
    def load_databases(cls, conf):
        try:
            for type in conf["DATABASE"]:
                if type != 'default':
                    cls.add_database(type, conf["DATABASE"][type])
                else:
                    cls.set_default_database(conf["DATABASE"][conf["DATABASE"][type]])
        except KeyError:
            cls.Databases = {}
        cls.__runtime_change = True

    @classmethod
    def add_database(cls, db_type, db_conf):
        db = cls.Databases.get(db_type, None)
        if db is None and cls.__runtime_change is False:
            cls.Databases[db_type] = db_conf
        elif db is not None:
            logging.warning("Database '%s' already set" % db_type)
        else:
            raise Exceptions.RuntimeExceptions.DatabaseChangeException(
                "Not permitted to change database '%s'  while app is running" % db_type
            )

    @classmethod
    def set_default_database(cls, db_conf):
        db = cls.Databases.get('default', None)
        if db is None and cls.__default_runtime_change is False:
            cls.Databases['default'] = db_conf
            cls.__default_runtime_change = True
        elif db is not None:
            logging.warning("Default database already set")
        else:
            raise Exceptions.RuntimeExceptions.DatabaseChangeException(
                "Not permitted to change default database while app is running"
            )

    @classmethod
    def load_logins(cls, conf):
        try:
            cls.Logins = conf['LOGINS']
        except KeyError as e:
            cls.Logins = {}

    @classmethod
    def add_login(cls, login_name, login_conf):
        login = cls.Logins.get(login_name, None)
        if login is None and cls.__login_change is False:
            cls.Logins[login_name] = login_conf
        elif login is not None:
            logging.warning("Database '%s' already set" % login_name)
        else:
            raise Exceptions.RuntimeExceptions.LoginChangeException(
                "Not permitted to change login method '%s'  while app is running" % login_name
            )

    @classmethod
    def set_default_login(cls, login_conf):
        login = cls.Logins.get('default', None)
        if login is None and cls.__default_login_change is False:
            cls.Logins['default'] = login_conf
            cls.__default_login_change = True
        elif login is not None:
            logging.warning("Default login already set")
        else:
            raise Exceptions.RuntimeExceptions.LoginChangeException(
                "Not permitted to change default login while app is running"
            )

    @classmethod
    def load_runtime(cls, conf):
        if cls.__srv_runtime is False:
            cls.SERVER_DATA = conf['SERVER_ENV']
            cls.__srv_runtime = True
        else:
            raise Exceptions.RuntimeExceptions.RuntimeException(
                "Not permitted to change server configuration data while app is running"
            )

    @classmethod
    def load_services(cls, conf):
        try:
            cls.Services = {}
            for service in conf['SERVICES']:
                cls.add_service(service, conf['SERVICES'][service])
        except KeyError:
            cls.Services = {}
        cls.__services_loaded = True

    @classmethod
    def add_service(cls, service_name, service_conf):
        db = cls.Services.get(service_name, None)
        if db is None and cls.__services_loaded is False:
            cls.Services[service_name] = service_conf
        elif db is not None:
            logging.warning("Service '%s' already set" % service_name)
        else:
            raise Exceptions.RuntimeExceptions.ServiceChangeException(
                "Not permitted to change service '%s' while app is running" % service_conf
            )
