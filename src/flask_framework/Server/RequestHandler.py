# coding: utf-8


__author__ = 'Frederick NEY'


class Init(object):

    def __init__(self, server):
        """

        :param server:
        :type server: flask.Flask
        """
        import logging
        server.before_request(self.before_request)
        server.teardown_request(self.after_request)
        try:
            from server.middleware import Middlewares
            Middlewares.init(server)
        except Exception as e:
            import os
            logging.warning("{}: {} in {}".format(__name__, e, os.getcwd()))
            try:
                from Server.Middleware import Middlewares
                Middlewares.init(server)
            except Exception as ie:
                import traceback
                logging.warning("{}: {} in {}".format(__name__, ie, os.getcwd()))

    def before_request(self, *args, **kwargs):
        import logging
        from flask import request
        logging.debug("Starting reply to request %s" % request.path)
        try:
            from server.middleware import Middlewares
            Middlewares.before_request(*args, **kwargs)
        except Exception as e:
            import os
            logging.warning("{}: {} in {}".format(__name__, e, os.getcwd()))
            try:
                from Server.Middleware import Middlewares
                Middlewares.before_request(*args, **kwargs)
            except Exception as ie:
                import traceback
                logging.warning("{}: {} in {}".format(__name__, ie, os.getcwd()))
        return

    def after_request(self, *args, **kwargs):
        import logging
        from flask import request
        try:
            from server.middleware import Middlewares
            Middlewares.after_request(*args, **kwargs)
        except Exception as e:
            import os
            logging.warning("{}: {} in {}".format(__name__, e, os.getcwd()))
            try:
                from Server.Middleware import Middlewares
                Middlewares.after_request(*args, **kwargs)
            except Exception as ie:
                import traceback
                logging.warning("{}: {} in {}".format(__name__, ie, os.getcwd()))
        logging.debug("Finishing reply to request %s" % request.path)
        return

    def auth_request(self, *args, **kwargs):
        return

    def admin_request(self, *args, **kwargs):
        return
