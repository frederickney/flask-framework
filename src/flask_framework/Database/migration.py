# coding: utf-8

__author__ = "Frederick NEY"

from flask_migrate import Migrate as Migration


class Migrate(object):
    __migrate: Migration = None

    @classmethod
    def run(cls, server, command):
        from .driver import Driver
        from flask_migrate import Migrate
        from flask_migrate import command
        for name, db in Driver.engines.items():
            try:
                migrate = Migrate(server, db, command=command)
            except AttributeError as e:
                continue
