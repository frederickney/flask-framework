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
"""

HTTP_DEFAULT_ENTRY = """class Route(object):
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
        server.add_url_rule('/', 'home', controllers.web.home.index, methods=["GET"])
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
"""

WS_ENTRY = """# coding: utf-8


class Handler(object):

    def __init__(self, socketio):
        \"\"\"

        :param socketio:
        :type socketio: flask_socketio.SocketIO
        \"\"\"
        import controllers
"""

PLUGINS_ENTRY = """# coding: utf-8


class Load(object):

    def __init__(self, srv, scheduler, session, csrf, socket):
        \"\"\"

        :param srv:
        :type srv: flask.Flask
        :param scheduler:
        :type scheduler: flask_apscheduler.APScheduler
        :param session:
        :type session: flask_session.Session | None
        :param csrf:
        :type csrf: flask_wtf.csrf.CSRFProtect | None
        :param socket:
        :type socket: flask_socketio.SocketIO
        \"\"\"
        import controllers
"""

MIDDLEWARE_ENTRY = """# coding: utf-8


class Load(object):

    def __init__(self, server):
        \"\"\"

        :param server:
        :type server: flask.Flask
        \"\"\"
        import controllers

        
class Middlewares(object):

    @classmethod
    def init(cls, server):
        \"\"\"

        :param server:
        :type server: flask.Flask
        \"\"\"
        return
    
    @classmethod
    def before_request(cls, *args, **kwargs):
        return
    
    @classmethod
    def after_request(cls, *args, **kwargs):
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

BASE_BLUEPRINT_CONTROLLER = """# coding: utf-8

from flask import Blueprint

bp = Blueprint("{PREFIX}", __name__, url_prefix="/{PREFIX}")

class Controller(object):
    \"\"\"
    {PREFIX} Controller

    Class that handles all kind of allowed operation on {PREFIX}.

    Usualy get is for retrieving content with optional filter arguments,  post is for writing content to backend.
    \"\"\"
    
    @staticmethod
    @bp.route('', methods=["get"])
    def retrieve():
        #TODO implement your code here 
        pass
    
    @staticmethod
    @bp.route('/add', methods=["post"])
    def create():
        #TODO implement your code here 
        pass
        
"""


BASE_HOME_CONTROLLER = """
class Controller(object):

    @staticmethod
    def index():
        return template("welcome.html")
"""

BASE_MIDDLEWARE = """
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

IMPORT_BLUEPRINT_CONTROLLER = "from .{} import bp as {}\n"


IMPORT_ERROR = "from .{} import http_{}\n"

IMPORT_MIDDLEWARE = "from .{} import {}\n"

HTTP_ERRORS = {
}


INSTALL_BLUEPRINT = """        {}.register_blueprint({})\n"""
INSTALL_PREFIXED_BLUEPRINT_DOC = """        #Rewrite prefix as -p has been used on blueprint installation it will override the blueprint url_prefix generated on blueprint creation\n"""
INSTALL_PREFIXED_BLUEPRINT = """        {}.register_blueprint({}, url_prefix="{}")\n"""
INSTALL_WEB_ROUTE = """        {}.add_url_rule("/{}", {}, name="ui.{}")\n"""
INSTALL_API_ROUTE = """        {}.add_url_rule("/api/{}", {}, name="api.{}")\n"""
INSTALL_WEBSOCKET_ROUTE = """        {}.on_event("socket.{}", {}, namespace="/socket/{}")\n"""
INSTALL_ERRORS_ROUTE= """        {}.register_error_handler({}, {})\n"""

FLASK_RENDERING_IMPORT = "from flask import render_template as template\n\n"

FLASK_FRAMEWORK_BASE_CONF = """SERVER:
    APP_NAME: {}
    APP_KEY: {}
    ENV: dev
    BIND:
        ADDRESS: localhost
        PORT: 4200
    STATIC_PATH: static
    TEMPLATE_PATH: template
    WORKERS: sync
    CAPTURE: true
    SESSION: filesystem
    THREADS_PER_CORE: 16
    LOG:
        DIR: log
        LEVEL: debug


SERVICES: 
  filesystem:
    PATH: sessions
"""

DATABASE_MODELS_IMPORTS = """from . import *\n"""
DATABASE_IMPORTS = """from . import {}\n"""