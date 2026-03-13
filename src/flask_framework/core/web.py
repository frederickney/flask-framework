# coding: utf-8


__author__ = 'Frederick NEY'


class Route(object):
    """
    Class that will configure all web based routes for the server
    """

    def __init__(self, srv):
        """
        Main entrypoint to load http routes rendering ui from working directory.
        Looks for server or Server module within working directory for any web or Web file containing
        a Route class or method inside.
        :param srv: FLask instance
        :type srv: flask.Flask
        :return: Route object
        :rtype: Route
        """
        import logging
        try:
            import server
            server.web.Route(srv)
        except Exception as e:
            import os
            logging.warning("{}: {} in {}".format(__name__, e, os.getcwd()))
            try:
                import Server
                Server.Web.Route(srv)
            except Exception as ie:
                import traceback
                logging.warning("{}: Fallback to default controller as: {} in {}".format(__name__, ie, os.getcwd()))
                import flask_framework.controllers as Controller
        return
