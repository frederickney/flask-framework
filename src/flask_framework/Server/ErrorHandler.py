# coding: utf-8


__author__ = 'Frederick NEY'
from flask_framework.Deprecation import module_deprecation
module_deprecation(__name__, __name__.lower().replace('errorhandler', 'errors').replace('server', 'core'), '1.3.0')

class Route(object):
    """
    Class that will configure all function used for handling requests error code
    """

    def __init__(self, srv):
        """
        Main entrypoint to load errors routes from working directory.
        Looks for server or Server module within working directory for any errorhandler or ErrorHandler file containing
        a Route class or method inside.
        :param srv: Flask instance
        :type srv: flask.Flask
        :return: Route object
        :rtype: Route
        """
        import logging
        import flask_framework.Controllers as Controllers
        srv.register_error_handler(404, Controllers.Web.HTTP40XController.page_or_error404)
        srv.register_error_handler(500, Controllers.Web.HTTP50XController.error500)
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
        return
