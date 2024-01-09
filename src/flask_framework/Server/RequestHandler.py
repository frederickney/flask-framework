# coding: utf-8


__author__ = 'Frederick NEY'


class Init(object):

    def __init__(self, server):
        """

        :param server:
        :type server: flask.Flask
        """
        server.before_request(self.before_request)
        server.teardown_request(self.after_request)

    def before_request(self, *args, **kwargs):
        import logging
        from flask import request
        from flask_framework.Database import Database
        Database.start_sessions()
        try:
            Database.session.begin()
        except Exception as e:
            logging.warning(e)
        try:
            for name, db in Database.sessions.items():
                db.begin()
        except Exception as e:
            logging.warning(e)
        logging.debug("Starting reply to request %s" % request.path)
        return

    def after_request(self, *args, **kwargs):
        import logging
        from flask_framework.Database import Database
        from flask import request
        try:
            Database.session.commit()
        except Exception as e:
            logging.warning(e)
        try:
            for name, db in Database.sessions.items():
                db.commit()
        except Exception as e:
            logging.warning(e)
        Database.close_sessions()
        logging.debug("Finishing reply to request %s" % request.path)
        return

    def auth_request(self, *args, **kwargs):
        return

    def admin_request(self, *args, **kwargs):
        return
