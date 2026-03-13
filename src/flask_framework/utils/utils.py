# coding: utf-8


__author__ = "Frederick NEY"

import os

from flask_framework.exceptions.runtime import web_denied
from . import templates
from .module import generate, create_project, create_server


@web_denied
def make_middleware(basepath, middleware):
    if not os.path.exists(os.path.join(os.path.join(basepath, 'server'), 'middleware.py')):
        fp = open(os.path.join(os.path.join(basepath, 'server'), 'middleware.py'), "w")
        fp.write(templates.PYTHON_FILE_HEAD)
    else:
        fp = open(os.path.join(os.path.join(basepath, 'server'), 'middleware.py'), "a")
    fp.write(templates.BASE_MIDDLEWARE.format(middleware))
    fp.close()
    pass


@web_denied
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


@web_denied
def make_project(basepath, project, inst_dir):
    create_project(basepath, project)
    create_server(project, os.path.join(basepath, project), inst_dir)
