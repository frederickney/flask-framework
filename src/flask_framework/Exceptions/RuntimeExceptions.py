# coding: utf-8


__author__ = 'Frederick NEY'
import functools
import warnings
from flask_framework.Deprecation import module_deprecation
module_deprecation(__name__, __name__.lower().replace('runtimeexceptions', 'runtime'), '1.3.0')


class RuntimeException(Exception):
    message = None

    def __init__(self, msg):
        self.message = "RuntimeException: " + msg
        super(RuntimeException, self).__init__(self.message)

    def __str__(self):
        return self.message


class DatabaseChangeException(RuntimeException):
    message = None

    def __init__(self, msg):
        self.message = "DatabaseChangeException: " + msg
        super(DatabaseChangeException, self).__init__(self.message)

    def __str__(self):
        return self.message


class LoginChangeException(RuntimeException):
    message = None

    def __init__(self, msg):
        self.message = "LoginChangeException: " + msg
        super(LoginChangeException, self).__init__(self.message)

    def __str__(self):
        return self.message


class ServiceChangeException(RuntimeException):
    message = None

    def __init__(self, msg):
        self.message = "DatabaseChangeException: " + msg
        super(ServiceChangeException, self).__init__(self.message)

    def __str__(self):
        return self.message



class WebDenyFunctionCall(DeprecationWarning):
    """
    Base class for disabling call of function.
    """

    def __init__(self, *args, **kwargs):  # real signature unknown
        super(WebDenyFunctionCall, self).__init__(*args, **kwargs)

    @staticmethod  # known case of __new__
    def __new__(*args, **kwargs):  # real signature unknown
        """ Create and return a new object.  See help(type) for accurate signature. """
        return args[1]


def web_denied(func):
    """Deprecation decorator which can be used to mark functions / classes
    as deprecated. It will result in a warning being emitted
    when the function is used."""

    @functools.wraps(func)
    def deny(*args, **kwargs):
        from flask import redirect
        from flask import request
        from flask import url_for
        if len(dir(request)) != 0:
            warnings.simplefilter('always', WebDenyFunctionCall)  # turn off filter
            warnings.warn("Access denied to function %s." % func.__name__, category=WebDenyFunctionCall, stacklevel=2)
            warnings.simplefilter('default', WebDenyFunctionCall)  # reset filter
            return redirect(request.referrer or url_for('home'))
        return func(*args, **kwargs)

    return deny
