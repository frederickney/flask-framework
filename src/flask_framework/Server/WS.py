# coding: utf-8


__author__ = 'Frederick NEY'


class Route(object):
    """
    Class that will configure all web services based routes for the server
    """
    def __init__(self, srv):
        """
        Constructor
        :param srv: Flask server
        :type srv: flask.Flask
        :return: Route object
        """
        import logging
        try:
            import server
            server.ws.Route(srv)
        except Exception as e:
            import os
            logging.warning("{}: {} in {}".format(__name__, e, os.getcwd()))
            try:
                import Server
                Server.WS.Route(srv)
            except Exception as ie:
                import traceback
                logging.warning("{}: Fallback to default controller as: {} in {}".format(__name__, ie, os.getcwd()))
                import flask_framework.Controllers as Controller
        return
