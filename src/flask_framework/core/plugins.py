# coding: utf-8


__author__ = 'Frederick NEY'


class Load(object):

    def __init__(cls, **kwargs):
        """
        Main entrypoint to load errors routes from working directory.
        Looks for server or Server module within working directory for any errorhandler or ErrorHandler file containing
        a Route class or method inside.
        :param srv: FastAPI instance
        :type srv: fastapi.FastAPI
        :return: Route object
        :rtype: Route
        """
        import logging
        try:
            import server
            server.plugins.Load(**kwargs)
        except Exception as e:
            import os
            logging.debug("{}: {} in {}".format(__name__, e, os.getcwd()))
        try:
            import Server
            Server.Plugins.Load(**kwargs)
        except Exception as e:
            import os
            logging.debug("{}: {} in {}".format(__name__, e, os.getcwd()))
        return
