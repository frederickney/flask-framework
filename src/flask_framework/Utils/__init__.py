# coding: utf-8


__author__ = "Frederick NEY"

from .module import generate
from .utils import make_controller, make_middleware, make_project
from flask_framework.Deprecation import module_deprecation
module_deprecation(__name__, __name__.lower().replace('server', 'core'), '1.3.0')
