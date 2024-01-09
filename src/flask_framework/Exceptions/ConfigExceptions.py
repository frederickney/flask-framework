# coding: utf-8


__author__ = 'Frederick NEY'


class ConfException(Exception):

    message = None

    def __init__(self, msg):
        self.message = "Configuration error: " + msg
        super(ConfException, self).__init__(self.message)

    def __str__(self):
        return self.message


class InvalidConfigurationFileError(ConfException):

    message = None

    def __init__(self, msg):
        self.message = "Configuration error: " + msg
        super(InvalidConfigurationFileError, self).__init__(self.message)

    def __str__(self):
        return self.message


class NotAConfigurationFileError(ConfException):

    message = None

    def __init__(self, msg):
        self.message = "Configuration error: " + msg
        super(NotAConfigurationFileError, self).__init__(self.message)

    def __str__(self):
        return self.message

