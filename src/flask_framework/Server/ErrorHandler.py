# coding: utf-8


__author__ = 'Frederick NEY'


class Route(object):
    """
    Class that will configure all function used for handling requests error code
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
            Server.ErrorHandler.Route(server)
        except Exception as e:
            logging.warning("ErrorHandler: Fallback to default error handler as : {}".format(e))
            import flask_framework.Controllers as Controllers
            server.register_error_handler(404, Controllers.Web.HTTP40XController.page_or_error404)
            server.register_error_handler(500, Controllers.Web.HTTP50XController.error500)
        return
