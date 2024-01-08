

class Handler(object):

    def __init__(self, socketio):
        """

        :param socketio:
        :type socketio: flask_socketio.SocketIO
        """
        import logging
        try:
            import Controllers
            import Server
            Server.Socket.Handler(socketio)
        except Exception as e:
            logging.warning("Socket: Fallback to default controller as : {}".format(e))
            import flask_framework.Controllers as Controller
