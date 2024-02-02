# coding: utf-8


__author__ = 'Frederick NEY'


class Load(object):

    def __init__(cls, **kwargs):
        """

        :param server:
        :type server: flask.Flask
        """
        import logging
        try:
            import server
            server.plugins.Load(*kwargs)
        except Exception as e:
            import os
            logging.debug("{}: {} in {}".format(__name__, e, os.getcwd()))
        try:
            import Server
            Server.Plugins.Load(*kwargs)
        except Exception as e:
            import os
            logging.debug("{}: {} in {}".format(__name__, e, os.getcwd()))
        return
