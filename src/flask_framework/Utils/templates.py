PYTHON_FILE_HEAD = '# coding: utf-8\n\n\n'

HTTP_ENTRY = """# coding: utf-8


class Route(object):
    \"\"\"
    Class that will configure all {} services based routes for the server
    \"\"\"
    def __init__(self, server):
        \"\"\"
        Constructor
        :param server: Flask server
        :type server: flask.Flask
        :return: Route object
        \"\"\"
        import controllers
        return
"""

HTTP_ERROR_HANDLER_ENTRY = """# coding: utf-8


class Route(object):
    \"\"\"
    Class that will configure all function used for handling requests error code
    \"\"\"

    def __init__(self, server):
        \"\"\"
        Constructor
        :param server: Flask server
        :type server: flask.Flask
        :return: Route object
        \"\"\"
        import controllers
{}
        return
"""

WS_ENTRY = """# coding: utf-8


class Handler(object):

    def __init__(self, socketio):
        \"\"\"

        :param socketio:
        :type socketio: flask_socketio.SocketIO
        \"\"\"
        import controllers
        return
"""

ERROR_ENTRY = """        server.register_error_handler({}, {})\n"""

BASE_ERROR = """
def http_{}(error):
    return template('{}.html', title=error)
"""

BASE_CONTROLLER = """# coding: utf-8


class Controller(object):

    @staticmethod
    def index():
        return
"""

BASE_MIDDLEWARE = """# coding: utf-8
class {}(object):

    @classmethod
    def use(cls):
        \"\"\"
        :return: call to the decorated function
        \"\"\"

        def using(func):
            def decorator(*args, **kwargs):

                result = func(*args, **kwargs)
                return result

            return decorator

        return using

"""

IMPORTS = "from . import {}\n"

IMPORT_CONTROLLER = "from .{} import Controller as {}\n"

IMPORT_ERROR = "from .{} import http_{}\n"

HTTP_ERRORS = {
    404: 'controllers.web.errors.http_404',
    500: 'controllers.web.errors.http_500'
}

FLASK_RENDERING_IMPORT = "from flask import render_template as template\n\n"
