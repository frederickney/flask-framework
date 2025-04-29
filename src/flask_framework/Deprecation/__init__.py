# coding: utf-8


__author__ = 'Frederick NEY'

import functools
import warnings


class OutdatedFunctionCall(DeprecationWarning):
    """
    Base class for warnings about features which is outdated.
    """

    def __init__(self, *args, **kwargs):  # real signature unknown
        super(OutdatedFunctionCall, self).__init__(*args, **kwargs)

    @staticmethod  # known case of __new__
    def __new__(*args, **kwargs):  # real signature unknown
        """ Create and return a new object.  See help(type) for accurate signature. """
        return args[1]


class DeprecatedFunctionCall(DeprecationWarning):
    """
    Base class for warnings about features which is deprecated.
    """

    def __init__(self, *args, **kwargs):  # real signature unknown
        super(DeprecatedFunctionCall, self).__init__(*args, **kwargs)

    @staticmethod  # known case of __new__
    def __new__(*args, **kwargs):  # real signature unknown
        """ Create and return a new object.  See help(type) for accurate signature. """
        return args[1]


class FutureRemovalFunctionCall(DeprecationWarning):
    """
    Base class for warnings about features which is deprecated.
    """

    def __init__(self, *args, **kwargs):  # real signature unknown
        super(FutureRemovalFunctionCall, self).__init__(*args, **kwargs)

    @staticmethod  # known case of __new__
    def __new__(*args, **kwargs):  # real signature unknown
        """ Create and return a new object.  See help(type) for accurate signature. """
        return args[1]


def class_deprecation(func):
    """Deprecation decorator which can be used to mark classes
    as deprecated. It will result in a warning being emitted
    when the class is used."""

    @functools.wraps(func)
    def deprecation(*args, **kwargs):
        warnings.simplefilter('always', DeprecatedFunctionCall)  # turn off filter
        warnings.warn("{} instead of function {}.".format(message, func.__name__), category=DeprecatedFunctionCall)
        warnings.warn("Call to deprecated function %s." % func.__name__, category=DeprecatedFunctionCall)
        warnings.simplefilter('default', DeprecatedFunctionCall)  # reset filter
        return func(*args, **kwargs)

    return deprecation


def class_outdated(func):
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


def deprecated(message='Using {function}'):
    """Deprecation decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""

    def using(func):

        @functools.wraps(func)
        def deprecation(*args, **kwargs):
            warnings.simplefilter('always', DeprecatedFunctionCall)  # turn off filter
            warnings.warn("{} instead of function {}.".format(message, func.__name__), category=DeprecatedFunctionCall)
            warnings.warn("Call to deprecated function %s." % func.__name__, category=DeprecatedFunctionCall, stacklevel=2)
            warnings.simplefilter('default', DeprecatedFunctionCall)  # reset filter
            return func(*args, **kwargs)

        return deprecation

    return using


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


class Future(object):

    @staticmethod
    def remove(version):
        """
        Future mark functions as removed.
        It will result in a error being emitted
        when the function is used.
        """
        def removed(func):
            @functools.wraps(func)
            def removal(*args, **kwargs):
                warnings.simplefilter('always', FutureRemovalFunctionCall)  # turn off filter
                warnings.warn(
                    "Call to function that will be removed on next minor release({}): {}.".format(
                        version,
                        func.__name__
                    ),
                    category=FutureRemovalFunctionCall,
                    stacklevel=2
                )
                warnings.simplefilter('default', FutureRemovalFunctionCall)  # reset filter
                return func(*args, **kwargs)

            return removal

        return removed