#!/usr/bin/python3
# coding: utf-8


__author__ = 'Frederick NEY'

import os

from flask_framework.Utils import make_controller, make_middleware, make_project


def parser():
    import argparse
    parser = argparse.ArgumentParser(description='Python FLASK server')
    parser.add_argument(
        '-cc', '--create-controller',
        help='Create controller',
        required=False
    )
    parser.add_argument(
        '-cm', '--create-middleware',
        help='Create middleware',
        required=False
    )
    parser.add_argument(
        '-cp', '--create-project',
        help='Create project',
        required=False
    )
    args = parser.parse_args()
    if args.create_project:
        make_project(os.getcwd(), args.create_project, os.path.dirname(os.path.realpath(__file__)))
        exit(0)
    elif args.create_controller:
        make_controller(os.getcwd(), args.create_controller)
        exit(0)
    elif args.create_middleware:
        make_middleware(os.getcwd(), args.create_middleware)
        exit(0)


if __name__ == '__main__':
    parser()
