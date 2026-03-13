# coding: utf-8


__author__ = 'Frederick NEY'
from flask_framework.Deprecation import module_deprecation
module_deprecation(__name__, __name__.lower().replace('server', 'core'), '1.3.0')


class Route(object):
    """
    Class that will configure all web services based routes for the server
    """

    def __init__(self, srv):
        """
        Main entrypoint to load http routes rendering ui from working directory.
        Looks for server or Server module within working directory for any ws or WS file containing
        a Route class or method inside.
        :param srv: Flask instance
        :type srv: flask.Flask
        :return: Route object
        :rtype: Route
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
