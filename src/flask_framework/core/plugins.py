# coding: utf-8


__author__ = 'Frederick NEY'


class Load(object):

    def __init__(cls, **kwargs):
        """
        Main entrypoint to load plugins from working directory.
        Looks for server or Server module within working directory for any plugins or Plugins file containing
        a Load class.
        :param srv: Flask instance
        :type srv: flask.Flask
        :param scheduler: APScheduler
        :type scheduler: flask_apscheduler.APScheduler
        :param session: Flask session
        :type session: flask_session.Session | None
        :param csrf: Flask CSRF middleware
        :type csrf: flask_wtf.CSRFProtect | None
        :param socket: flask socket io
        :type socket: flask_socketio.SocketIO
        :return: Load object
        :rtype: Load
        """
        import logging
        try:
            import server
            server.plugins.Load(**kwargs)
        except Exception as e:
            import os
            logging.debug("{}: {} in {}".format(__name__, e, os.getcwd()))
            try:
                import Server
                Server.Plugins.Load(**kwargs)
            except Exception as e:
                import os
                logging.debug("{}: {} in {}".format(__name__, e, os.getcwd()))
        return
