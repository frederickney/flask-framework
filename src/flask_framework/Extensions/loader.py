# coding: utf-8


__author__ = "Frédérick NEY"

__version__ = "0.0.1"

import importlib
import logging
import os
import re

import flask_framework.Exceptions as Exceptions
from flask_framework.Config import Environment

_pattern = '^([a-zA-Z]+(_[a-zA-Z]+)*)$'

version = __version__

_dir_to_mod = lambda fp: os.path.splitext(fp)[0]


def modules_loader(package):
    """
    
    Used to load modules from the application extensions module
    :param package: name of the application extensions module
    :type package: str
    """
    search = re.compile(_pattern, re.IGNORECASE)
    mod_dir = filter(search.search, os.listdir(os.path.join(os.curdir, package)))
    plugins = map(_dir_to_mod, mod_dir)
    importlib.import_module(package)
    for plugin in plugins:
        print(plugin)
        if not plugin.startswith('__'):
            load(package, plugin)
    return


def modules_reloader(package):
    """
    
    Used to reload modules from the application extensions module
    :param package: name of the application extensions module
    :type package: str
    """
    search = re.compile(_pattern, re.IGNORECASE)
    mod_dir = filter(search.search, os.listdir(os.path.join(os.curdir, package)))
    plugins = map(_dir_to_mod, mod_dir)
    imported = importlib.import_module(package)
    importlib.reload(imported)
    for plugin in plugins:
        if not plugin.startswith('__'):
            reload(package, plugin)


def load(package, ext):
    """
    
    Used to load extention from the application extensions module
    :param package: name of the application extensions module
    :type package: str
    :param ext: name of the extension
    :type ext: str
    """
    importlib.import_module(package)
    return importlib.import_module('{}.{}'.format(package, ext))


def reload(package, ext):
    """
    
    Used to reload extention from the application extensions module
    :param package: name of the application extensions module
    :type package: str
    :param ext: name of the extension
    :type ext: str
    """
    importlib.import_module(package)
    imported_mod = importlib.import_module('{}.{}'.format(package, ext))
    logging.info('Module "%s" reload...' % ext)
    imported_mod = importlib.reload(imported_mod)
    try:
        imported_mod.reload()
        logging.info('Module "%s" reloaded' % ext)
    except AttributeError as e:
        logging.debug(e)
        logging.info('No reload for module "%s"' % ext)
        pass
    except NameError as e:
        logging.debug(e)
        logging.info('Error in module "%s"' % ext)
        pass
    return imported_mod


def routes_loader(package, app):
    """

    Used to load routes for each registered extensions
    :param package: name of the application extensions module
    :type package: str
    :param app: flask base application
    :type app: flask.Flask
    :return :
    """
    research = re.compile(_pattern, re.IGNORECASE)
    if 'extensions' in Environment.SERVER_DATA:
        if os.path.exists(os.path.join(os.path.join(os.curdir, Environment.SERVER_DATA['extensions']['GlobalPath']))):
            mods_dir = filter(
                research.search,
                os.listdir(
                    os.path.join(
                        os.path.join(
                            os.curdir,
                            Environment.SERVER_DATA['extensions']['GlobalPath']
                        ),
                        package
                    )
                )
            )
        else:
            mods_dir = filter(research.search, os.listdir(os.path.join(os.curdir, package)))
        mods = map(_dir_to_mod, mods_dir)
        importlib.import_module(package)
        for mod in mods:
            if not mod.startswith('__'):
                load_routes(package, mod, app)
    return


def load_routes(package, ext, app):
    """

    Used to load routes for the given registered extension
    :param package: name of the application extensions module
    :type package: str
    :param ext: name of the extension
    :type ext: str
    :param app: flask base application
    :type app: flask.Flask
    :return :
    """
    try:
        imported_mod = importlib.import_module(
            '{}.{}'.format(package, ext)
        ).register_routes(app)
        logging.info('Routes for "%s" loaded' % ext.split('.')[1])
    except AttributeError as e:
        logging.debug(e)
        logging.info('No routes for module "%s"' % ext.split('.')[1])
        pass
    except NameError as e:
        logging.debug(e)
        logging.info('Error in module "%s"' % ext.split('.')[1])
        pass
    except Exceptions.RuntimeExceptions.RuntimeException as e:
        logging.debug(e)
        logging.info('Routes already loaded for module "%s"' % ext.split('.')[1])
        pass


def blueprints_loader(package, app):
    """

    Used to load blueprints for each registered extensions
    :param package: name of the application extensions module
    :type package: str
    :param app: flask base application
    :type app: flask.Flask
    :return :
    """
    research = re.compile(_pattern, re.IGNORECASE)
    if 'extensions' in Environment.SERVER_DATA:
        if os.path.exists(os.path.join(os.path.join(os.curdir, Environment.SERVER_DATA['extensions']['GlobalPath']))):
            mods_dir = filter(
                research.search,
                os.listdir(
                    os.path.join(
                        os.path.join(
                            os.curdir,
                            Environment.SERVER_DATA['extensions']['GlobalPath']
                        ),
                        package
                    )
                )
            )
        else:
            mods_dir = filter(research.search, os.listdir(os.path.join(os.curdir, package)))
        exts = map(_dir_to_mod, mods_dir)
        importlib.import_module(package)
        for ext in exts:
            if not ext.startswith('__'):
                load_blueprints(package, ext, app)
    return


def load_blueprints(package, ext, app):
    """

    Used to load blueprints for the given registered extension
    :param package: name of the application extensions module
    :type package: str
    :param ext: name of the extension
    :type ext: str
    :param app: flask base application
    :type app: flask.Flask
    :return :
    """
    try:
        imported_mod = importlib.import_module(
            '{}.{}'.format(package, ext)
        ).register_blueprints(app)
        logging.info('Blueprints for "%s" loaded' % ext.split('.')[1])
    except AttributeError as e:
        logging.debug(e)
        logging.info('No blueprints for module "%s"' % ext.split('.')[1])
        pass
    except NameError as e:
        logging.debug(e)
        logging.info('Error in module "%s"' % ext.split('.')[1])
        pass
    except Exceptions.RuntimeExceptions.RuntimeException as e:
        logging.debug(e)
        logging.info('Blueprints already loaded for module "%s"' % ext.split('.')[1])
        pass


def init_modules(package, db):
    """
    
    Used for initializing extensions on request. Must be used into a middleware. 
    In order to use, all your extension must implement an <extension>.loaded property that will tell if it is already loaded to enchance performances. 
    If not present your extension will be loaded on every single request.  
    :param package: name of the application extensions module
    :type package: str 
    :param db: driver to databases similar to Database.Database
    :type db: Database.driver.Driver
    :return:
    """
    research = re.compile(_pattern, re.IGNORECASE)
    if 'extensions' in Environment.SERVER_DATA:
        if os.path.exists(os.path.join(os.path.join(os.curdir, Environment.SERVER_DATA['extensions']['GlobalPath']))):
            mods_dir = filter(
                research.search,
                os.listdir(
                    os.path.join(
                        os.path.join(
                            os.curdir, Environment.SERVER_DATA['extensions']['GlobalPath']
                        ),
                        package
                    )
                )
            )
        else:
            mods_dir = filter(research.search, os.listdir(os.path.join(os.curdir, package)))
        mods = map(_dir_to_mod, mods_dir)
        importlib.import_module(package)
        for mod in mods:
            if not mod.startswith('__'):
                init_module(package, mod, db)
    return


def init_module(package, ext, db):
    """
    
    Used for initializing extension. 
    In order to use, all your extension must implement an <extension>.loaded property that will tell if it is already loaded to enchance performances. 
    If not present your extension will be loaded on every single call.  
    Notice it will end up generating exceptions or errors because of the routes / blueprints that will be also loaded.
    :param package: name of the application extensions module
    :type package: str 
    :param ext: name of the extension
    :type ext: str
    :param db: driver to databases similar to Database.Database
    :type db: Database.driver.Driver
    :return:
    """
    try:
        imported_mod = importlib.import_module(
            '{}.{}'.format(package, ext)
        )
        if not 'loaded' in dir(imported_mod):
            imported_mod.init(db)
        elif not imported_mod.loaded:
            imported_mod.init(db)
        logging.info('Module "%s" initialized' % ext.split('.')[1])
    except AttributeError as e:
        logging.debug(e)
        logging.info('No initialization for module "%s"' % ext.split('.')[1])
        pass
    except NameError as e:
        logging.debug(e)
        logging.info('Error in module "%s"' % ext.split('.')[1])
        pass
    except Exceptions.ConfigExceptions.ConfException as e:
        logging.debug(e)
        logging.info('Initialization already done for module "%s"' % ext.split('.')[1])
        pass


def installer(module):
    import pip
    try:
        if 'extensions' in Environment.SERVER_DATA:
            if 'BaseModule' in Environment.SERVER_DATA['extensions']:
                packages = importlib.import_module(
                    '{}.{}'.format(
                        Environment.SERVER_DATA['extensions']['BaseModule'],
                        module
                    )
                ).Loader.packages()
            else:
                logging.warning(
                    "{}: extensions.BaseModule not configured in section SERVER_ENV in {}".format(
                        __name__,
                        os.environ.get('CONFIG_FILE', "/etc/server/config.json")
                    )
                )
        else:
            packages = importlib.import_module(module).Loader.packages()
        for package in packages:
            pip.main(['install', package])
        logging.info('Packages for "%s" installed' % module)
    except ImportError as e:
        logging.warning(
            "{}: {} not found in {}".format(
                __name__,
                (
                    module if 'extensions' not in Environment.SERVER_DATA
                    else
                    '{}.{}'.format(
                        Environment.SERVER_DATA['extensions']['BaseModule'],
                        module
                    ) if 'BaseModule' in Environment.SERVER_DATA['extensions']
                    else
                    module
                ),
                os.getcwd()
            )
        )
    except AttributeError as e:
        logging.debug(e)
        logging.info('No package dependencies for module "%s"' % module)
    except NameError as e:
        logging.debug(e)
        logging.info('Error in module "%s"' % module)


def installer(module):
    import pip
    try:
        packages = []
        if 'extensions' in Environment.SERVER_DATA:
            if 'BaseModule' in Environment.SERVER_DATA['extensions']:
                packages = importlib.import_module(
                    '{}.{}.{}'.format(
                        Environment.SERVER_DATA['extensions']['BaseModule'],
                        module,
                        'Loader'
                    )
                ).packages()
            else:
                logging.warning(
                    "{}: extensions.BaseModule not configured in section SERVER_ENV in {}".format(
                        __name__,
                        os.environ.get('CONFIG_FILE', "/etc/server/config.json")
                    )
                )
        else:
            packages = importlib.import_module("{}.{}".format(module, 'Loader')).packages()
        for package in packages:
            pip.main(['install', package])
        logging.info('Packages for "%s" installed' % module)
    except ImportError as e:
        logging.warning(
            "{}: {} not found in {}".format(
                __name__,
                (
                    module if 'extensions' not in Environment.SERVER_DATA
                    else
                    '{}.{}'.format(
                        Environment.SERVER_DATA['extensions']['BaseModule'],
                        module
                    ) if 'BaseModule' in Environment.SERVER_DATA['extensions']
                    else
                    module
                ),
                os.getcwd()
            )
        )
    except AttributeError as e:
        logging.debug(e)
        logging.info('No package dependencies for module "%s"' % module)
    except NameError as e:
        logging.debug(e)
        logging.info('Error in module "%s"' % module)


def module(module):
    try:
        if 'extensions' in Environment.SERVER_DATA:
            if 'BaseModule' in Environment.SERVER_DATA['extensions']:
                return importlib.import_module(
                    '{}.{}'.format(Environment.SERVER_DATA['extensions']['BaseModule'], module)
                )
            else:
                logging.warning("{}: extensions.BaseModule not configured in section SERVER_ENV in {}".format(
                    __name__,
                    os.environ.get('CONFIG_FILE', "/etc/server/config.json"))
                )
        else:
            return importlib.import_module(module)
    except ImportError as e:
        logging.warning(
            "{}: {} not found in {}".format(
                __name__,
                (
                    module if 'extensions' not in Environment.SERVER_DATA
                    else
                    '{}.{}'.format(
                        Environment.SERVER_DATA['extensions']['BaseModule'],
                        module
                    )
                    if 'BaseModule' in Environment.SERVER_DATA['extensions']
                    else
                    module
                ),
                os.getcwd()
            )
        )
    return None
