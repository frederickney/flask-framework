# coding: utf-8


__author__ = 'Frederick NEY'
from flask_framework.Deprecation import module_deprecation
module_deprecation(__name__, __name__.lower().replace('queryexceptions', 'query'), '1.3.0')


class BaseException(Exception):
    message = None

    def __init__(self, msg):
        self.message = "QUERY ERROR: " + msg
        super(BaseException, self).__init__(self.message)

    def __str__(self):
        return self.message


class PrimaryKeyChangeException(BaseException):
    message = None

    def __init__(self, msg):
        self.message = "Primary key change: " + msg
        super(PrimaryKeyChangeException, self).__init__(self.message)

    def __str__(self):
        return self.message
