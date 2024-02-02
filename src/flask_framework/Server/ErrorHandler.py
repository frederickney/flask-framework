# coding: utf-8


__author__ = 'Frederick NEY'


class Route(object):
    """
    Class that will configure all function used for handling requests error code
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
            server.errorhandler.Route(srv)
        except Exception as e:
            import os
            logging.warning("{}: {} in {}".format(__name__, e, os.getcwd()))
            try:
                import Server
                Server.ErrorHandler.Route(srv)
            except Exception as e:
                logging.warning("{}: Fallback to default error handler as : {} in {}".format(__name__, e, os.getcwd()))
                import flask_framework.Controllers as Controllers
                srv.register_error_handler(404, Controllers.Web.HTTP40XController.page_or_error404)
                srv.register_error_handler(500, Controllers.Web.HTTP50XController.error500)
        return
