# coding: utf-8

__author__ = "Frederick NEY"


from flask_migrate import Migrate as Migration, MigrateCommand
from flask_script import Manager

class Migrate(object):

    __migrate: Migration = None

    @classmethod
    def migration(cls, server, models, db):
        if models is not 'default':
            import importlib
            importlib.import_module('Models.Persistent.%s' % models)
        cls.__migrate.init_app(server, db)

    @classmethod
    def run(cls, server):
        cls.__migrate = Migration()
        from .driver import Driver
        for name, session in Driver._sqlalchemy_array.items():
            if name is not 'default':
                import importlib
                importlib.import_module('Models.Persistent.%s' % name)
            cls.migration(server, name, session)
        manager = Manager(server)
        manager.add_command('db', MigrateCommand)
        manager.run()
