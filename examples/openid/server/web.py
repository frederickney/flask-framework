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
        import controllers
        server.add_url_rule("/test", 'test', controllers.web.login.Controller.test, methods=["GET"])
        controllers.web.openid.Controller.setup(server)
        return
