# coding: utf-8


__author__ = 'Frederick NEY'


class Loader(object):
    __loaded__ = False

    @classmethod
    def load(cls):
        from . import loader
        from flask_framework.Database import Database
        from flask_framework.Server import Process
        import logging
        logging.info('Loading plugins')
        loader.moduleloader('extensions')
        loader.initmodule('extensions', db=Database)
        loader.routesloader('extensions', app=Process.get())
        loader.blueprintsloader('extensions', app=Process.get())
        cls.__loaded__ = True
        logging.info('Plugins loaded')
        return

    @classmethod
    def reload(cls):
        from . import loader
        from flask_framework.Database import Database
        from flask_framework.Server import Process
        import logging
        logging.info('Reloading plugins')
        loader.modulereloader('extensions')
        loader.initmodule('extensions', db=Database)
        loader.routesloader('extensions', app=Process.get())
        loader.blueprintsloader('extensions', app=Process.get())

    @classmethod
    def loaded(cls):
        return cls.__loaded__


def all():
    import re
    import os
    import importlib
    from flask_framework.Config import Environment
    research = re.compile('^([^.pyc]|[^__pycache__]|[^.py])*$', re.IGNORECASE)
    mods_dir = filter(
        research.search,
        os.listdir(os.path.join(Environment.SERVER_DATA['extensions']['GlobalPath'], 'extensions'))
    )
    form_module = lambda fp: '.' + os.path.splitext(fp)[0]
    mods = map(form_module, mods_dir)
    importlib.import_module('extensions')
    modules = []
    for mod in mods:
        if not mod.startswith('__'):
            modules.append(mod.split('.')[1])
    return modules


def load():
    Loader.load() if not Loader.loaded() else Loader.reload()
