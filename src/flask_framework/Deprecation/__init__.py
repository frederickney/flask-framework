# coding: utf-8


__author__ = 'Frederick NEY'


import warnings
import functools


class OutdatedFunctionCall(DeprecationWarning):
    """
    Base class for warnings about features which is outdated.
    """
    def __init__(self, *args, **kwargs): # real signature unknown
        super(OutdatedFunctionCall, self).__init__(*args, **kwargs)

    @staticmethod # known case of __new__
    def __new__(*args, **kwargs): # real signature unknown
        """ Create and return a new object.  See help(type) for accurate signature. """
        return args[1]


class DeprecatedFunctionCall(DeprecationWarning):
    """
    Base class for warnings about features which is deprecated.
    """
    def __init__(self, *args, **kwargs): # real signature unknown
        super(DeprecatedFunctionCall, self).__init__(*args, **kwargs)

    @staticmethod # known case of __new__
    def __new__(*args, **kwargs): # real signature unknown
        """ Create and return a new object.  See help(type) for accurate signature. """
        return args[1]


def deprecated(func):
    """Deprecation decorator which can be used to mark functions / classes
    as deprecated. It will result in a warning being emitted
    when the function is used."""
    @functools.wraps(func)
    def deprecation(*args, **kwargs):
        warnings.simplefilter('always', DeprecatedFunctionCall)  # turn off filter
        warnings.warn("Call to deprecated function %s." % func.__name__, category=DeprecatedFunctionCall, stacklevel=2)
        warnings.simplefilter('default', DeprecatedFunctionCall)  # reset filter
        return func(*args, **kwargs)

    return deprecation


def outdated(func):
    """Outdated decorator which can be used to mark functions
    as obsolete. It will result in a error being emitted
    when the function is used."""
    @functools.wraps(func)
    def obsolete(*args, **kwargs):
        warnings.simplefilter('always', OutdatedFunctionCall)  # turn off filter
        warnings.warn("Call to outdated function %s." % func.__name__, category=OutdatedFunctionCall, stacklevel=2)
        warnings.simplefilter('default', OutdatedFunctionCall)  # reset filter
        return func(*args, **kwargs)

    return obsolete