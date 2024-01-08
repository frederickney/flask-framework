# coding: utf-8

__author__ = 'Frederick NEY'


class Route(object):
    """
    Class that will configure all web services based routes for the server
    """
    def __init__(self, server):
        """
        Constructor
        :param server: Flask server
        :type server: flask.Flask
        :return: Route object
        """
        import logging
        try:
            import Controllers
            import Server
            Server.Web.Route(server)
        except Exception as e:
            logging.warning("WS: Fallback to default controller as : {}".format(e))
            import flask_framework.Controllers as Controller
        return
