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
        :return: Route object
        """
        import Controllers
        server.add_url_rule('/', "home", Controllers.Web.HomeController.default, methods=["GET"])
        return

