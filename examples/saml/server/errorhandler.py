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
        import controllers
        server.register_error_handler(404, controllers.web.HTTP40XController.page_or_error404)
        server.register_error_handler(500, controllers.web.HTTP50XController.error500)
        return
