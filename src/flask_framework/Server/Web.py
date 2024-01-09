# coding: utf-8


__author__ = 'Frederick NEY'


class Route(object):
    """
    Class that will configure all web based routes for the server
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
            import Server
            Server.Web.Route(server)
        except Exception as e:
            import traceback
            logging.warning("Web: Fallback to default controller as : {}".format(e))
            logging.debug(traceback.print_exc())
            import flask_framework.Controllers as Controller
        return
