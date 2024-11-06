try:
    from flask import request

    loaded = True
except ImportError:
    loaded = False

import functools
import warnings


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
    @functools.wraps(func)
    def deny(*args, **kwargs):
        from flask import redirect
        from flask import request
        if len(dir(request)) != 0:
            warnings.simplefilter('always', WebDenyFunctionCall)  # turn off filter
            warnings.warn("Access denied to function %s." % func.__name__, category=WebDenyFunctionCall, stacklevel=2)
            warnings.simplefilter('default', WebDenyFunctionCall)  # reset filter
            return redirect(request.referrer)
        return func(*args, **kwargs)

    return deny
