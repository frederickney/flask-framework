# coding: utf-8


__author__ = 'Frederick NEY'


class Handler(object):

    def __init__(self, socketio):
        """
        Main entrypoint to load websockets from working directory.
        Looks for server or Server module within working directory for any socket or Socket file containing
        a Handler class.
        :param socketio: SocketIO instance
        :type socketio: flask_socketio.SocketIO
        :return: Handler object
        :rtype: Load
        """
        import logging
        try:
            import server
            server.socket.Handler(socketio)
        except Exception as e:
            import os
            logging.warning("{}: {} in {}".format(__name__, e, os.getcwd()))
            try:
                import Server
                Server.Socket.Handler(socketio)
            except Exception as ie:
                import traceback
                logging.warning("{}: Fallback to default controller as: {} in {}".format(__name__, ie, os.getcwd()))
                import flask_framework.controllers as Controller
        return
