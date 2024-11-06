# coding: utf-8


__author = "Frederick NEY"

import os
import shutil
from uuid import uuid5, uuid4, NAMESPACE_URL

from flask_framework.Server import deniedwebcall
from . import templates


@deniedwebcall
def create_dir(basepath, dir):
    if not os.path.exists(os.path.join(basepath, dir)):
        os.mkdir(os.path.join(basepath, dir), 0o755)
        while not os.path.exists(os.path.join(basepath, dir)):
            ("Waiting for path creation")


@deniedwebcall
def create_project(basepath, project):
    if not os.path.exists(os.path.join(basepath, project)):
        create_dir(basepath, project)

    create_dir(os.path.join(basepath, project), 'controllers')
    generate(os.path.join(basepath, project), "{}/{}".format('controllers', 'web'))
    create_dir(os.path.join(basepath, project), 'server')
    generate(os.path.join(basepath, project), "{}/{}".format('server', 'web'))


@deniedwebcall
def generate(basepath, module, sub_module=None):
    if not os.path.exists(os.path.join(basepath, os.path.dirname(module))):
        generate(
            basepath, "/".join(
                [module.split('/')[i] for i in range(0, len(module.split('/')) - 1)]), module.split('/')[-1]
        )
        os.mkdir(os.path.join(basepath, os.path.dirname(module)), 0o755)
        while not os.path.exists(os.path.join(basepath, os.path.dirname(module))):
            "Waiting for path creation"
    if sub_module is not None:
        if os.path.exists(
                os.path.join(os.path.join(basepath, os.path.dirname(module)), '__init__.py')
        ):
            fp = open(
                os.path.join(os.path.join(basepath, os.path.dirname(module)), '__init__.py'),
                "a"
            )
            fp.write(templates.IMPORTS.format(module.split("/")[-1]))
            fp.close()
        else:
            fp = open(
                os.path.join(os.path.join(basepath, os.path.dirname(module)), '__init__.py'),
                "w"
            )
            fp.write(templates.PYTHON_FILE_HEAD)
            fp.write(templates.IMPORTS.format(module.split("/")[-1]))
            fp.close()
    else:
        if not os.path.exists(
                os.path.join(os.path.join(basepath, os.path.dirname(module)), '__init__.py')
        ):
            fp = open(
                os.path.join(os.path.join(basepath, os.path.dirname(module)), '__init__.py'),
                "w"
            )
            fp.write(templates.PYTHON_FILE_HEAD)
            fp.close()


@deniedwebcall
def try_copy(src, dst):
    """

    :param src:
    :param dst:
    :return:
    """
    if not os.path.exists(dst):
        shutil.copytree(src, dst)


@deniedwebcall
def try_copy_templates(_inst_dir, path):
    """

    :param _inst_dir:
    :param path:
    :return:
    """
    try_copy(os.path.join(_inst_dir, 'template'), os.path.join(path, 'template'))


@deniedwebcall
def try_copy_statics(_inst_dir, path):
    """

    :param _inst_dir:
    :param path:
    :return:
    """
    try_copy(os.path.join(_inst_dir, 'static'), os.path.join(path, 'static'))


@deniedwebcall
def try_create_errors(path):
    pass


@deniedwebcall
def try_create_entry(path, entry):
    if os.path.exists(os.path.join(path, 'server')):
        if not os.path.exists(os.path.join(os.path.join(path, 'server'), '{}.py'.format(entry))):
            fp = open(os.path.join(os.path.join(path, 'server'), '{}.py'.format(entry)), 'w')
            fp.write(templates.HTTP_ENTRY.format(entry))
            fp.close()
            fp = open(os.path.join(os.path.join(path, 'server'), '__init__.py'), 'a')
            fp.write(templates.IMPORTS.format(entry))
            fp.close()


@deniedwebcall
def try_create_web_entry(path):
    if os.path.exists(os.path.join(path, 'server')):
        if not os.path.exists(os.path.join(os.path.join(path, 'server'), '{}.py'.format('web'))):
            generate(path, 'controllers/web/home')
            fp = open(os.path.join(path, '{}.py'.format('controllers/web/home')), 'w')
            fp.write(templates.PYTHON_FILE_HEAD)
            fp.write(templates.FLASK_RENDERING_IMPORT)
            fp.write(templates.BASE_HOME_CONTROLLER.format('welcome'))
            fp.close()
            fp = open(
                os.path.join(
                    os.path.dirname(os.path.join(path, '{}.py'.format('controllers/web/home'))),
                    "__init__.py"
                ),
                'a'
            )
            fp.write(templates.IMPORT_CONTROLLER.format('home', 'home'))
            fp.close()
            fp = open(os.path.join(os.path.join(path, 'server'), '{}.py'.format('web')), 'w')
            fp.write(templates.HTTP_DEFAULT_ENTRY.format('web'))
            fp.close()
            fp = open(os.path.join(os.path.join(path, 'server'), '__init__.py'), 'a')
            fp.write(templates.IMPORTS.format('web'))
            fp.close()


@deniedwebcall
def try_create_error_controller(path):
    if os.path.exists(os.path.join(path, 'server')):
        if not os.path.exists(os.path.join(os.path.join(path, 'server'), '{}.py'.format('errorhandler'))):
            content = ''
            for code, error in templates.HTTP_ERRORS.items():
                generate(path, error.replace('.', '/'))
                content += templates.ERROR_ENTRY.format(code, error)
                fp = open(os.path.join(path, '{}.py'.format(error.replace('.', '/'))), 'w')
                fp.write(templates.PYTHON_FILE_HEAD)
                fp.write(templates.FLASK_RENDERING_IMPORT)
                fp.write(templates.BASE_ERROR.format(code, code))
                fp.close()
                fp = open(
                    os.path.join(
                        os.path.dirname(os.path.join(path, '{}.py'.format(error.replace('.', '/')))),
                        "__init__.py"
                    ),
                    'a'
                )
                fp.write(templates.IMPORT_ERROR.format(os.path.basename(error.replace('.', '/')), code))
                fp.close()
            fp = open(os.path.join(os.path.join(path, 'server'), '{}.py'.format('errorhandler')), 'w')
            fp.write(templates.HTTP_ERROR_HANDLER_ENTRY.format(content))
            fp.close()
            fp = open(os.path.join(os.path.join(path, 'server'), '__init__.py'), 'a')
            fp.write(templates.IMPORTS.format('errorhandler'))
            fp.close()
    pass


@deniedwebcall
def try_create_ws_entry(path):
    try_create_entry(path, 'ws')


def try_create_default_conf(path, project):
    if not os.path.exists(os.path.join(path, 'config')):
        os.mkdir(os.path.join(path, 'config'), 0o755)
    if not os.path.exists(os.path.join(os.path.join(path, 'config'), 'config.yml')):
        fp = open(os.path.join(os.path.join(path, 'config'), 'config.yml'), 'w')
        fp.write(templates.FLASK_FRAMEWORK_BASE_CONF.format(project, str(uuid5(NAMESPACE_URL, str(uuid4())))))
        fp.close()


@deniedwebcall
def try_create_socket_entry(path):
    if os.path.exists(os.path.join(path, 'server')):
        if not os.path.exists(os.path.join(os.path.join(path, 'server'), '{}.py'.format('socket'))):
            fp = open(os.path.join(os.path.join(path, 'server'), '{}.py'.format('socket')), 'w')
            fp.write(templates.WS_ENTRY)
            fp.close()
            fp = open(os.path.join(os.path.join(path, 'server'), '__init__.py'), 'a')
            fp.write(templates.IMPORTS.format('socket'))
            fp.close()


@deniedwebcall
def create_server(project, path, _inst_dir):
    if not os.path.exists(os.path.join(path, 'server')):
        create_dir(path, 'server')
    if not os.path.exists(os.path.join(os.path.join(path, 'server'), '__init__.py')):
        fp = open(
            os.path.join(os.path.join(path, 'server'), '__init__.py'),
            "w"
        )
        fp.write(templates.PYTHON_FILE_HEAD)
        fp.close()
    try_create_errors(path)
    try_create_error_controller(path)
    try_create_web_entry(path)
    try_copy_statics(_inst_dir, path)
    try_copy_templates(_inst_dir, path)
    try_create_default_conf(path, project)
