import os
import sys
import logging
import multiprocessing
from flask_framework.database import Database
from flask_framework.config import Environment
from flask_framework.core import Process


class Logging:
    logging_dir_exist = False
    _loglevel = 'warning'

    @classmethod
    def set_loglevel(cls, loglevel):
        cls._loglevel = loglevel

    @classmethod
    def get_loglevel(cls):
        return cls._loglevel
    

class BaseApp:
    def __init__(self):
        if len(Environment.Databases) > 0:
            logging.debug("Connecting to database(s)...")
            Database.register_engines(echo=Environment.SERVER['CAPTURE'])
            Database.init()
            logging.debug("Database(s) connected...")

    @staticmethod
    def load_app():
        Process.init(tracking_mode=False)
        logging.debug("Server initialized...")
        Process.load_plugins()
        logging.debug("Loading server routes...")
        Process.load_routes()
        Process.load_middleware()
        logging.debug("Server routes loaded...")
        logging.debug("Loading websocket events")
        Process.load_socket_events()
        logging.debug("Websocket events loaded...")
        # app.teardown_appcontext(Database.save)
        logging.info("Server is now ready...")

def number_of_workers():
        """
        Return the number of worker processes. Based on th cpu count times 2
        """
        return multiprocessing.cpu_count() * 2
