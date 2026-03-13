# coding: utf-8


__author__ = 'Frederick NEY'


class Load(object):

    def __init__(self, srv):
        """
        Main entrypoint to load middlewares from working directory.
        Looks for server or Server module within working directory for any middleware or Middleware file containing
        a Load class or method inside.
        :param srv: Flask instance
        :type srv: flask.Flask
        :return: Load object
        :rtype: Load
        """
        import logging
        try:
            import server
            server.middleware.Load(srv)
        except Exception as e:
            import os
            logging.debug("{}: {} in {}".format(__name__, e, os.getcwd()))
        try:
            import Server
            Server.Middleware.Load(srv)
        except Exception as e:
            import os
            logging.debug("{}: {} in {}".format(__name__, e, os.getcwd()))
        return
