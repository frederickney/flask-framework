# coding: utf-8


__author__ = 'Frederick NEY'


class Load(object):

    def __init__(self, server):
        """

        :param server:
        :type server: flask.Flask
        """
        import logging
        try:
            import Server
            Server.Middleware.Load(server)
        except Exception as e:
            logging.warning("Middleware: Fallback to default middleware as : {}".format(e))
        return
