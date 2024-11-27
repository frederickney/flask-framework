# coding: utf-8
import logging
from functools import wraps

from flask import current_app
from flask import request
from flask_login.config import EXEMPT_METHODS
from flask_login.utils import current_user

__author__ = 'Frederick NEY'


def admin_login_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        try:
            logging.info("{}: user {} admin_role {}".format(
                __name__,
                getattr(current_user, 'email', None),
                getattr(current_user, 'is_admin', False)
            ))
        except AttributeError as e:
            logging.info("{}: annonymous".format(__name__))

        if request.method in EXEMPT_METHODS or current_app.config.get("LOGIN_DISABLED"):
            pass
        elif not current_user.is_authenticated:
            logging.info("{}: annonymous".format(__name__))
            return current_app.login_manager.unauthorized()
        elif (current_user.is_authenticated and not hasattr(current_user, 'is_admin')):
            logging.info("{}: user {} admin_role {}".format(__name__, getattr(current_user, 'email', None)))
            return current_app.login_manager.unauthorized()
        elif (current_user.is_authenticated and not current_user.is_admin):
            logging.warning("{}: user {} admin_role {}".format(__name__, current_user.email, current_user.is_admin))
            return current_app.login_manager.unauthorized()
        # flask 1.x compatibility
        # current_app.ensure_sync is only available in Flask >= 2.0
        if callable(getattr(current_app, "ensure_sync", None)):
            return current_app.ensure_sync(func)(*args, **kwargs)
        return func(*args, **kwargs)

    return decorated
