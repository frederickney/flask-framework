# coding: utf-8


__author__ = 'Frederick NEY'

import os
import logging
import sqlalchemy
import warnings

from .driver import Driver
from flask_framework.Deprecation import deprecated, outdated, class_outdated


def _rollback():
    for session in Driver.sessions:
        try:
            session.rollback()
        except Exception as e:
            logging.error(e)
    try:
        Driver.session.rollback()
    except Exception as e:
        logging.error(e)
        raise e


def safe(func):

    def decorated(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except sqlalchemy.exc.PendingRollbackError as e:
            logging.warning(e)
            _rollback() 
            return func(*args, **kwargs)
        except sqlalchemy.exc.OperationalError as e:
            logging.warning(e)
            Driver.reconnect_all()
            return func(*args, **kwargs)

    return decorated


@class_outdated
class Database(object):
    cls: object = None

    @outdated
    def load(self, cls):
        """
        :deprecated : will be removed on version 1.2.0
        """
        def decorator(*args, **kwargs):
            instance = cls(*args, **kwargs)
            self.cls = instance
            return instance

        return decorator

    @deprecated(f'Use {__package__}.{os.path.basename(__file__).removesuffix(".py")}.safe')
    def use(self, databases=['default']):
        self.load()
        def using(func):
            return safe(func)

        return using

    @staticmethod
    @deprecated(f'Use {__package__}.{os.path.basename(__file__).removesuffix(".py")}.safe')
    def use_db(databases=['default']):

        def using(func):
            return safe(func)

        return using

    @staticmethod
    @deprecated(f'Use {__package__}.{os.path.basename(__file__).removesuffix(".py")}.safe')
    def safe_use_db(databases=['default']):
        def using(func):
            return safe(func)

        return using
