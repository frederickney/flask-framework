# coding: utf-8


__author__ = "Frederick NEY"

import os

from flask_framework.Server import deniedwebcall
from . import templates
from .module import generate, create_project, create_server


@deniedwebcall
def make_auth():
    pass


@deniedwebcall
def make_middleware(basepath, middleware):
    if not os.path.exists(os.path.join(os.path.join(basepath, 'server'), 'middleware.py')):
        fp = open(os.path.join(os.path.join(basepath, 'server'), 'middleware.py'), "w")
        fp.write(templates.PYTHON_FILE_HEAD)
    else:
        fp = open(os.path.join(os.path.join(basepath, 'server'), 'middleware.py'), "a")
    fp.write(templates.BASE_MIDDLEWARE.format(middleware))
    fp.close()
    pass


@deniedwebcall
def make_controller(basepath, controller):
    generate(basepath, controller)
    fp = open(
        os.path.join(os.path.join(basepath, os.path.dirname(controller)), "{}.py".format(os.path.basename(controller))),
        "w"
    )
    fp.write(templates.BASE_CONTROLLER)
    fp.close()
    fp = open(
        os.path.join(os.path.join(basepath, os.path.dirname(controller)), '__init__.py'),
        "a"
    )
    fp.write(templates.IMPORT_CONTROLLER.format(
        os.path.basename(controller), os.path.basename(controller)
    ))
    fp.close()


@deniedwebcall
def make_project(basepath, project, inst_dir):
    create_project(basepath, project)
    create_server(project, os.path.join(basepath, project), inst_dir)
