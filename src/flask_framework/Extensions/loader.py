# coding: utf-8


__author__ = "Frederick NEY"


import importlib
import logging
import os
import re
import sys

import flask_framework.Exceptions as Exceptions
from flask_framework.Config import Environment


def moduleloader(module):
    """

    :param str module:
    :return:
    """
    research = re.compile('^([^.pyc]|[^__pycache__]|[^.py])*$', re.IGNORECASE)
    if 'extensions' in Environment.SERVER_DATA:
        if os.path.exists(os.path.join(os.path.join(os.curdir, Environment.SERVER_DATA['extensions']['GlobalPath']))):
            mods_dir = filter(research.search, os.listdir(os.path.join(os.path.join(os.curdir, Environment.SERVER_DATA['extensions']['GlobalPath']), module)))
        else:
            mods_dir = filter(research.search, os.listdir(os.path.join(os.curdir, module)))
        form_module = lambda fp : '.' + os.path.splitext(fp)[0]
        mods = map(form_module, mods_dir)
        importlib.import_module(module)
        for mod in mods:
            if not mod.startswith('__'):
                importlib.import_module(mod, package=module)
    return


def modulereloader(module):
    """

    :param str module:
    :return:
    """
    research = re.compile('^([^.pyc]|[^__pycache__]|[^.py])*$', re.IGNORECASE)
    if 'extensions' in Environment.SERVER_DATA:
        if os.path.exists(os.path.join(os.path.join(os.curdir, Environment.SERVER_DATA['extensions']['GlobalPath']))):
            mods_dir = filter(research.search, os.listdir(os.path.join(os.path.join(os.curdir, Environment.SERVER_DATA['extensions']['GlobalPath']), module)))
        else:
            mods_dir = filter(research.search, os.listdir(os.path.join(os.curdir, module)))
        form_module = lambda fp : '.' + os.path.splitext(fp)[0]
        mods = map(form_module, mods_dir)
        imported_mod = importlib.import_module(module)
        imported_mod = importlib.reload(imported_mod)
        for mod in mods:
            if not mod.startswith('__'):
                imported_mod = importlib.import_module(mod, package=module)
                imported_mod = importlib.reload(imported_mod)
                try:
                    imported_mod.reload()
                    logging.info('Module "%s" reloaded' % mod.split('.')[1])
                except AttributeError as e:
                    logging.debug(e)
                    logging.info('No reload for module "%s"' % mod.split('.')[1])
                    continue
                except NameError as e:
                    logging.debug(e)
                    logging.info('Error in module "%s"' % mod.split('.')[1])
                    continue
    return


def initmodule(module, db):
    """

    :param str module:
    :param Database.driver.Driver db:
    :return:
    """
    research = re.compile('^([^.pyc]|[^__pycache__]|[^.py])*$', re.IGNORECASE)
    if 'extensions' in Environment.SERVER_DATA:
        if os.path.exists(os.path.join(os.path.join(os.curdir, Environment.SERVER_DATA['extensions']['GlobalPath']))):
            mods_dir = filter(research.search, os.listdir(os.path.join(os.path.join(os.curdir, Environment.SERVER_DATA['extensions']['GlobalPath']), module)))
        else:
            mods_dir = filter(research.search, os.listdir(os.path.join(os.curdir, module)))
        form_module = lambda fp: '.' + os.path.splitext(fp)[0]
        mods = map(form_module, mods_dir)
        importlib.import_module(module)
        for mod in mods:
            if not mod.startswith('__'):
                try:
                    importlib.import_module(mod, package=module).init(db)
                    logging.info('Module "%s" initialized' % mod.split('.')[1])
                except AttributeError as e:
                    logging.debug(e)
                    logging.info('No initialization for module "%s"' % mod.split('.')[1])
                    continue
                except NameError as e:
                    logging.debug(e)
                    logging.info('Error in module "%s"' % mod.split('.')[1])
                    continue
                except Exceptions.ConfigExceptions.ConfException as e:
                    logging.debug(e)
                    logging.info('Initialization already done for module "%s"' % mod.split('.')[1])
                    continue
    return


def routesloader(module, app):
    """

    :param str module:
    :param flask.Flask app:
    :return :
    """
    research = re.compile('^([^.pyc]|[^__pycache__]|[^.py])*$', re.IGNORECASE)
    if 'extensions' in Environment.SERVER_DATA:
        if os.path.exists(os.path.join(os.path.join(os.curdir, Environment.SERVER_DATA['extensions']['GlobalPath']))):
            mods_dir = filter(research.search, os.listdir(os.path.join(os.path.join(os.curdir, Environment.SERVER_DATA['extensions']['GlobalPath']), module)))
        else:
            mods_dir = filter(research.search, os.listdir(os.path.join(os.curdir, module)))
        form_module = lambda fp: '.' + os.path.splitext(fp)[0]
        mods = map(form_module, mods_dir)
        importlib.import_module(module)
        for mod in mods:
            if not mod.startswith('__'):
                try:
                    importlib.import_module(mod, package=module).register_routes(app)
                    logging.info('Routes for "%s" loaded' % mod.split('.')[1])
                except AttributeError as e:
                    logging.debug(e)
                    logging.info('No routes for module "%s"' % mod.split('.')[1])
                    continue
                except NameError as e:
                    logging.debug(e)
                    logging.info('Error in module "%s"' % mod.split('.')[1])
                    continue
                except Exceptions.RuntimeExceptions.RuntimeException as e:
                    logging.debug(e)
                    logging.info('Routes already loaded for module "%s"' % mod.split('.')[1])
                    continue
    return


def blueprintsloader(module, app):
    """

    :param str module:
    :param flask.Flask app:
    :return:
    """
    research = re.compile('^([^.pyc]|[^__pycache__]|[^.py])*$', re.IGNORECASE)
    if 'extensions' in Environment.SERVER_DATA:
        if os.path.exists(os.path.join(os.path.join(os.curdir, Environment.SERVER_DATA['extensions']['GlobalPath']))):
            mods_dir = filter(research.search, os.listdir(os.path.join(os.path.join(os.curdir, Environment.SERVER_DATA['extensions']['GlobalPath']), module)))
        else:
            mods_dir = filter(research.search, os.listdir(os.path.join(os.curdir, module)))
        form_module = lambda fp: '.' + os.path.splitext(fp)[0]
        mods = map(form_module, mods_dir)
        importlib.import_module(module)
        for mod in mods:
            if not mod.startswith('__'):
                try:
                    importlib.import_module(mod, package=module).register_blueprints(app)
                    logging.info('Blueprints for "%s" loaded' % mod.split('.')[1])
                except AttributeError as e:
                    logging.debug(e)
                    logging.info('No blueprints for module "%s"' % mod.split('.')[1])
                    continue
                except NameError as e:
                    logging.debug(e)
                    logging.info('Error in module "%s"' % mod.split('.')[1])
                    continue
                except Exceptions.RuntimeExceptions.RuntimeException as e:
                    logging.debug(e)
                    logging.info('Blueprints already loaded for module "%s"' % mod.split('.')[1])
                    continue
    return


def installer(module):
    import pip
    try:
        pakages = importlib.import_module('Extensions.%s' % module).Loader.pakages()
        for package in pakages:
            pip.main(['install', package])
        logging.info('Packages for "%s" installed' % module)
    except AttributeError as e:
        logging.debug(e)
        logging.info('No package dependencies for module "%s"' % module)
    except NameError as e:
        logging.debug(e)
        logging.info('Error in module "%s"' % module)


def module(module):
    return importlib.import_module('Extensions.%s' % module)
