# coding: utf-8


__author__ = 'Frederick NEY'


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