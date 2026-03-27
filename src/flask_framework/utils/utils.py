# coding: utf-8


__author__ = "Frederick NEY"

import os
import logging
import inspect
import importlib
import re

from flask_framework.exceptions.runtime import web_denied
from . import templates
from .module import generate, create_project, create_server


@web_denied
def make_middleware(basepath, middleware):
    generate(basepath, f"middlewares/{middleware.lower()}", skip_root_level_init=True)
    if not os.path.exists(os.path.join(os.path.join(basepath, 'middlewares'), f'{middleware.lower()}.py')):
        logging.debug(f'Generating middlewares/{middleware.lower()}.py...')
        fp = open(os.path.join(os.path.join(basepath, 'middlewares'), f'{middleware.lower()}.py'), "w")
        fp.write(templates.PYTHON_FILE_HEAD)
    else:
        logging.debug(f'Updating middlewares/{middleware.lower()}.py...')
        fp = open(os.path.join(os.path.join(basepath, 'middlewares'), f'{middleware.lower()}.py'), "a")
    fp.write(templates.BASE_MIDDLEWARE.format(os.path.basename(middleware)))
    fp.close()
    logging.debug(f'Updating middlewares/{os.path.dirname(middleware)}/__init__.py...')
    fp = open(
        os.path.join(os.path.join(basepath, 'middlewares',  os.path.dirname(middleware)), '__init__.py'),
        "a"
    )
    fp.write(templates.PYTHON_FILE_HEAD)
    fp.write(templates.IMPORT_MIDDLEWARE.format(
        os.path.basename(middleware).lower().replace('/', '.'), os.path.basename(middleware)
    ))
    fp.close()
    pass


@web_denied
def make_controller(basepath, controller, blueprint=False):
    generate(basepath, controller)
    logging.debug(f'Generating {controller}.py...')
    fp = open(
        os.path.join(os.path.join(basepath, os.path.dirname(controller)), "{}.py".format(os.path.basename(controller))),
        "w"
    )
    if not blueprint:
        fp.write(templates.BASE_CONTROLLER)
    else: 
        fp.write(templates.BASE_BLUEPRINT_CONTROLLER.format(PREFIX=controller.split('/')[-1]))
    fp.close()
    logging.debug(f'Updating {os.path.dirname(controller)}/__init__.py...')
    fp = open(
        os.path.join(os.path.join(basepath, os.path.dirname(controller)), '__init__.py'),
        "a"
    )
    if not blueprint:
        fp.write(templates.IMPORT_CONTROLLER.format(
            os.path.basename(controller), os.path.basename(controller)
        ))
    else:
        fp.write(templates.IMPORT_BLUEPRINT_CONTROLLER.format(
            os.path.basename(controller), os.path.basename(controller)
        ))
    fp.close()


@web_denied
def make_project(basepath, project, inst_dir):
    create_project(basepath, project)
    create_server(project, os.path.join(basepath, project), inst_dir)


def _install_router(basepath, controller, type, prefix=None):
    """
    install controllers containing static and class methods
    :param basepath: str path like
    :type basepath: str
    :param controller: str path like
    :type controller: str
    :param type: type of route (web, ws or socket) 
    :type type: str
    """
    logging.debug(f'Reading server/{type}.py...')
    fd = open(f'server/{type}.py', 'r')
    content = fd.read() 
    fd.close()
    if content.endswith('return\n'):
        _content = content[:-15]
        _ends = content[-15:]
    else:
        _content = content
        _ends = ''
    if not prefix:
        logging.debug(f'Adding server/{templates.INSTALL_BLUEPRINT.format('server', controller.replace('/', '.')).replace('\n', '')}...')
        new_content = f"{_content}{templates.INSTALL_BLUEPRINT.format('server', controller.replace('/', '.'))}{_ends}"
    else:
        bp = importlib.import_module(controller.replace('/', '.'))
        logging.debug(f'Adding server/{templates.INSTALL_PREFIXED_BLUEPRINT.format('server', controller.replace('/', '.'), f"{prefix}{bp.url_prefix.replace('/', '') if prefix.endswith('/') else bp.url_prefix}").replace('\n', '')}...')
        new_content = f"{_content}{ templates.INSTALL_PREFIXED_BLUEPRINT.format('server', controller.replace('/', '.'), prefix)}{_ends}"
    logging.debug(f'Saving server/{type}.py...')
    fd = open(f'server/{type}.py', 'w')
    fd.write(new_content)
    fd.close()
    pass


def _install_controller(basepath, controller, methods, type):
    """
    install controllers containing static and class methods
    :param basepath: str path like
    :type basepath: str
    :param controller: str path like
    :type controller: str
    :param methods: methods list
    :type methods: list[str]
    :param type: type of route (web, ws or socket) 
    :type type: str
    """
    logging.debug(f'Reading server/{type}.py...')
    fd = open(f'server/{type}.py', 'r')
    content = fd.read() 
    fd.close()
    if content.endswith('return\n'):
        _content = content[:-15]
        _ends = content[-15:]
    else:
        _content = content
        _ends = ''
    new_content = f"{_content}"
    for method in methods:
        if type == 'ws':
            logging.debug(f'Adding server/{templates.INSTALL_PREFIXED_BLUEPRINT.format('server', f"{os.path.basename(controller)}/{method}", f"{controller.replace('/', '.')}.{method}", f"{os.path.basename(controller)}.{method}").replace('\n', '')}...')
            new_content += templates.INSTALL_API_ROUTE.format('server', f"{os.path.basename(controller)}/{method}", f"{controller.replace('/', '.')}.{method}", f"{os.path.basename(controller)}.{method}")
        elif type =='socket':
            logging.debug(f'Adding {templates.INSTALL_WEBSOCKET_ROUTE.format('server', f"{os.path.basename(controller)}/{method}", f"{controller.replace('/', '.')}.{method}", f"{os.path.basename(controller)}.{method}").replace('\n', '')}...')
            new_content += templates.INSTALL_WEBSOCKET_ROUTE.format('server', f"{os.path.basename(controller)}/{method}", f"{controller.replace('/', '.')}.{method}", f"{os.path.basename(controller)}.{method}")
        elif type == 'errorhandler':
            e_code = re.findall('(\\d+)', method)[0]
            logging.debug(f'Adding server/{templates.INSTALL_ERRORS_ROUTE.format('server', e_code, f"{controller.replace('/', '.')}.{method}").replace('\n', '')}...')
            new_content += templates.INSTALL_ERRORS_ROUTE.format('server', e_code, f"{controller.replace('/', '.')}.{method}")
        else: 
            logging.debug(f'Adding server/{templates.INSTALL_WEB_ROUTE.format('server', f"{os.path.basename(controller)}/{method}", f"{controller.replace('/', '.')}.{method}", f"{os.path.basename(controller)}.{method}").replace('\n', '')}...')
            new_content += templates.INSTALL_WEB_ROUTE.format('server', f"{os.path.basename(controller)}/{method}", f"{controller.replace('/', '.')}.{method}", f"{os.path.basename(controller)}.{method}")
    new_content += f"{_ends}"
    logging.debug(f'Saving server/{type}.py...')
    fd = open(f'server/{type}.py', 'w')
    fd.write(new_content)
    fd.close()
    pass


@web_denied
def install_routes(basepath, controller, type, prefix=None):
    import sys
    sys.path.append(basepath)
    if os.path.exists(os.path.join(basepath, os.path.dirname(controller))):
        module = importlib.import_module(controller.replace('/', '.'))
        if 'bp' in dir(module):
            logging.debug(f'Installing router {controller}...')
            #TODO edit server/{type}.py to install router
            _install_router(basepath, controller, type, prefix=prefix)
        elif 'Controller' in dir(module):
            logging.debug(f'Installing controller {controller}...')
            #TODO edit server/{type}.py to install controller by looping on static or class method
            methods = [
                func for func in dir(module.Controller) 
                if ( inspect.isfunction(getattr(module.Controller, func)) or inspect.ismethod(getattr(module.Controller, func))) and not func.startswith('_')
            ]
            _install_controller(basepath, controller, methods, type)
        else: 
            print('Unable to install {} routes'.format(controller))
    else:
        print('Unable to install {} routes'.format(controller))