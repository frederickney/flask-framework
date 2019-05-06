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
        from Config import Environment
        server.add_url_rule("/", "Flask", Controllers.Web.HomeController.default, methods=["GET"])
        return
