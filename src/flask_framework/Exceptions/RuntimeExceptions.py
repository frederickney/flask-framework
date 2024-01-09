# coding: utf-8


__author__ = 'Frederick NEY'


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
