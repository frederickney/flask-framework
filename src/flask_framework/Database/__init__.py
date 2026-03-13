# coding: utf-8


__author__ = 'Frederick NEY'

from flask_framework.Deprecation import module_deprecation
module_deprecation(__name__, __name__.lower(), '1.3.0')
from .driver import Driver as Database
from .decorators import safe