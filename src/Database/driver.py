# coding: utf-8

__author__ = 'Frederick NEY'

from Deprecation import deprecated


class Driver(object):

    engine = None
    session = None
    Model = None
    Managers = []

    @classmethod
    def setup(cls, app, driver, user, pwd, host, db, echo=False):
        """
        Setup function that will configure all the required resources for communicating with the database
        :param app: Flask server
        :param driver: Database driver that will be used when the server need to store persistant data
        :param user: Database user
        :param pwd: Database password
        :param host: Database host
        :param db: Database schema
        :param echo: Boolean for printing sql request default: false
        :return: N/A
        """
        from sqlalchemy import create_engine
        from sqlalchemy.orm import scoped_session, sessionmaker
        from sqlalchemy.ext.declarative import declarative_base
        database_uri = driver + '://' + user + ':' + pwd + '@' + host + '/' + db + '?charset=utf8'
        app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
        cls.engine = create_engine(database_uri, echo=echo)
        cls.session = sessionmaker(bind=cls.engine)
        cls.session = scoped_session(cls.session)
        cls.Model = declarative_base(cls.session)
        cls.Model.query = cls.session.query_property()

    @classmethod
    @deprecated
    def add_thread_manager(cls, manager_thread):
        """
        Deprecated! Function that start threads beside the server
        :param manager_thread: Thread object
        :return: N/A
        """
        from threading import Thread
        if manager_thread is not None:
            if isinstance(manager_thread, Thread):
                manager_thread.start()
                cls.Managers.append(manager_thread)

    @classmethod
    def add_task_db_session(cls, task_name):
        """
        Function that setup a different session for scheduling task
        :param task_name: The name of the task
        :return:
        """
        from sqlalchemy.orm import scoped_session, sessionmaker
        session = sessionmaker(bind=cls.engine)
        session = scoped_session(session)
        setattr(Driver, task_name, session)

    @classmethod
    def get_task_session(cls, task_name):
        return getattr(Driver, task_name, None)

    @classmethod
    def init(cls):
        """
        Function that create schema tables based on imported models within this function
        :return: N/A
        """
        cls.Model.metadata.create_all(bind=cls.engine)

    @staticmethod
    @deprecated
    def shutdown_session(exception=None):
        """
        Function that means to be used for ending database session before the server will be shut down
        :param exception:
        :return: N/A
        """
        import logging
        logger = logging.getLogger("GLOBAL")
        logger.info("Shutting down server...")
        for manager in Driver.Managers:
            manager.teardown = True
            manager.join(10)
            if manager.is_alive():
                logger.warning("Unable to properly stop thread '%s'" % manager.getName())
        Driver.session.remove()
        logger.info("Server is now shut down...")

