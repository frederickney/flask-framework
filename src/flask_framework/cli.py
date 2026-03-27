#!/usr/bin/python3
# coding: utf-8


__author__ = 'Frederick NEY'

import argparse
import os
import sys

from flask_framework.utils import make_controller, make_middleware, make_project, install_routes, create_database_models_modules
from flask_framework.config import Environment


def app_parser(parser):
    database_parser = parser.add_parser('database', help='Usage:\npython -m fastapi_framework_mvc.cli database -h', formatter_class=argparse.RawTextHelpFormatter)
    database_parser.add_argument(
        '-i', '--init',
        help='Create base sqlalchemy database models module for database-connector-kit python module\nThis can be also linked to alembic database migration python module.',
        required=True,
        action='store_true'
    )




def parser():
    parser = argparse.ArgumentParser(description='FastAPI Framework MVC CLI', formatter_class=argparse.RawTextHelpFormatter)
    action = parser.add_subparsers(dest='action')
    project_parser = action.add_parser('project', help='Usage:\npython -m fastapi_framework_mvc.cli project -h', formatter_class=argparse.RawTextHelpFormatter)
    project_parser.add_argument(
        '-c', '--create', 
        help='name of the project\nExample:\npython -m fastapi_framework_mvc.cli project --create webapp', 
        required=True,
        metavar='NAME'
    )
    controller_parser = action.add_parser('controller', help='Usage:\npython -m fastapi_framework_mvc.cli controller -h', formatter_class=argparse.RawTextHelpFormatter)
    controller_parser.add_argument(
        '-c', '--create', 
        help='Create controller\nexample:\npython -m fastapi_framework_mvc.cli controller --create controllers/web/login', 
        required=True, 
        metavar='NAME'
    )
    controller_parser.add_argument(
        '-blueprint', '--blueprint-mode', 
        help='Create a blueprint base controller', 
        default=False, 
        action='store_true', 
        required=False
    )
    middleware_parser = action.add_parser('middleware', help='Usage:\npython -m fastapi_framework_mvc.cli middleware -h', formatter_class=argparse.RawTextHelpFormatter)
    middleware_parser.add_argument(
        '-c', '--create', 
        help='Create middleware\nexample:\npython -m fastapi_framework_mvc.cli middleware --create my_middleware', 
        required=True, 
        metavar='NAME'
    )
    manager_parser = action.add_parser('manager', help='Usage:\npython -m fastapi_framework_mvc.cli manager -h', formatter_class=argparse.RawTextHelpFormatter)
    manager_parser.add_argument(
        '-l', '--link-controller', 
        help='manage app routes\nexample:\npython -m fastapi_framework_mvc.cli manager --link-controller controllers/web/login', 
        required=True
    )
    manager_parser.add_argument(
        '-p', '--prefix', 
        help='api prefix (only for api endpoints)', 
        required=False,
        default=None
    )
    if len(Environment.Databases.keys()) > 0:
        app_parser(action)
    args = parser.parse_args()
    if args.action == 'project':
        make_project(os.getcwd(), args.create, os.path.dirname(os.path.realpath(__file__)))
        exit(0)
    elif args.action == 'controller':
        controller = args.create
        if sys.platform.startswith('win') or sys.platform.startswith('nt'):
            controller = controller.replace('\\', '/')
        if controller.startswith('./'):
            controller = controller.removeprefix('./')
        make_controller(os.getcwd(), controller, blueprint=args.blueprint_mode)
        exit(0)
    elif args.action == "middleware":
        middleware = args.create
        if sys.platform.startswith('win') or sys.platform.startswith('nt'):
            middleware = middleware.replace('\\', '/')
        if middleware.startswith('./'):
            middleware = middleware.removeprefix('./')
        make_middleware(os.getcwd(), middleware)
        exit(0)
    elif args.action == "manager":
        controller = args.link_controller
        if sys.platform.startswith('win') or sys.platform.startswith('nt'):
            controller = controller.replace('\\', '/')
        if controller.startswith('./'):
            controller = controller.removeprefix('./')
        install_routes(
            os.getcwd(),
            controller, 
            type=
            'ws' if 'controllers/ws/' in controller else 
            'socket' if 'controllers/socket/' in controller else
            'errorhandler' if 'errors' in controller else 'web',
            prefix=args.prefix
        )
        exit(0)
    elif len(Environment.Databases.keys()) > 0:
        if args.action == "database":
            create_database_models_modules(os.getcwd(), Environment.Databases)
            exit(0)


if __name__ == '__main__':
    parser()
