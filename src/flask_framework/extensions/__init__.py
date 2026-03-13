# coding: utf-8


__author__ = 'Frederick NEY'

import pathlib


class Loader(object):
    __loaded__ = False

    @classmethod
    def load(cls, _ext=None):
        from . import loader
        from flask_framework.database import Database
        from flask_framework.core import Process
        import logging
        logging.info('Loading plugins')
        loader.modules_loader(_ext or 'extensions')
        loader.init_modules(_ext or 'extensions', db=Database)
        loader.routes_loader(_ext or 'extensions', app=Process.get())
        loader.blueprints_loader(_ext or 'extensions', app=Process.get())
        cls.__loaded__ = True
        logging.info('Plugins loaded')
        return

    @classmethod
    def reload(cls, _ext=None):
        from . import loader
        from flask_framework.database import Database
        from flask_framework.core import Process
        import logging
        logging.info('Reloading plugins')
        loader.modules_reloader(_ext or 'extensions')
        loader.init_modules(_ext or 'extensions', db=Database)
        loader.routes_loader(_ext or 'extensions', app=Process.get())
        loader.blueprints_loader(_ext or 'extensions', app=Process.get())

    @classmethod
    def loaded(cls):
        return cls.__loaded__


def all(_ext=None):
    import re
    import os
    import importlib
    from flask_framework.config import Environment
    research = re.compile(
        '^([a-zA-Z]+(_[a-zA-Z]+)*)$',
        re.IGNORECASE
    )
    if os.path.exists(
            os.path.join(Environment.SERVER.get('extensions', {}).get('path', os.getcwd()), _ext or 'extensions')
    ):
        mods_dir = filter(
            research.search,
            os.listdir(
                os.path.join(Environment.SERVER.get('extensions', {}).get('path', os.getcwd()), _ext or 'extensions'))
        )
    else:
        mods_dir = []
    form_module = lambda fp: '.' + os.path.splitext(fp)[0]
    mods = map(form_module, mods_dir)
    modules = []
    for mod in mods:
        if not mod.startswith('__'):
            modules.append(mod.split('.')[1])
    return modules


def load():
    from flask_framework.config import Environment
    if pathlib.Path(Environment.SERVER.get('extensions', {}).get('path', 'extensions')).is_dir():
        ext = Environment.SERVER.get('extensions', {}).get('path', 'extensions')
        Loader.load(ext) if not Loader.loaded() else Loader.reload(ext)
