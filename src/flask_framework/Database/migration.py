# coding: utf-8

__author__ = "Frederick NEY"


from flask_migrate import Migrate as Migration


class Migrate(object):

    __migrate: Migration = None


    @classmethod
    def run(cls, server):
        from .driver import Driver
        from flask_migrate import Migrate
        from flask_migrate import command
        from flask_script import Manager
        manager = Manager(server)
        manager.add_command('database', command)
        for name, db in Driver.engines.items():
            try:
                migrate = Migrate(server, db)
                manager.run()
            except AttributeError as e:
                continue
        if len(Driver.engines) == 0:
            manager.run()
