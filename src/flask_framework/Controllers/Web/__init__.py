# coding: utf-8


__author__ = "Frederick NEY"

from . import HTTP40XController, HTTP50XController
from flask_framework.Deprecation import module_deprecation
module_deprecation(__name__, __name__.lower(), '1.3.0')
