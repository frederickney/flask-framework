# coding: utf-8


__author__ = 'Frederick NEY'

import os
import logging
import sqlalchemy

from .driver import Driver
from ..Deprecation import deprecated


def _rollback():
    """
    Doing rollback
    """
    for session in Driver.sessions:
        try:
            session.rollback()
        except Exception as e:
            logging.error(e)
    try:
        Driver.session.rollback()
    except Exception as e:
        logging.error(e)


@deprecated(message='Use fastapi_framework_mvc.database.safe')
def safe(func):
    """
    Secure database connections on disconnection or pending rollback other a specific function.
    :param func: The function to secure
    :type func: callable
    :return: The result of the function
    :type func: any
    """
    def decorated(*args, **kwargs):
        """
        Retrieving functions arguments
        :param args: The arguments
        :type args: tuple[any]
        :param kwargs: The keyword arguments
        :type kwargs: dict[str, any]
        """
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
