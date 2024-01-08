# coding: utf-8

__author__ = 'Frederick NEY'

import logging
from .driver import Driver



class Database(object):
    cls: object = None

    def load(self, cls):

        def decorator(*args, **kwargs):
            instance = cls(*args, **kwargs)
            self.cls = instance
            return instance

        return decorator

    def use(self, databases=['default']):

        def using(func):
            def decorator(*args, **kwargs):
                logging.info('connecting')
                sessions = dict()
                for db_name in databases:
                    sessions[db_name] = Driver.start_session_by_name(db_name)
                setattr(self.cls, 'sessions', sessions)
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    logging.error(e)
                    result = None
                logging.info(self.cls)
                for name, session in sessions.items():
                    session.close()

                logging.info('disconnecting')
                return result

            return decorator

        return using

    @staticmethod
    def use_db(databases=['default']):
        def using(func):
            def decorator(*args, **kwargs):
                logging.info('connecting')
                sessions = dict()
                for db_name in databases:
                    sessions[db_name] = Driver.start_session_by_name(db_name)
                    kwargs.setdefault('sessions', sessions)
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    logging.error(e)
                    result = None
                for name, session in sessions.items():
                    session.close()

                logging.info('disconnecting')
                return result

            return decorator

        return using

