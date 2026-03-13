# coding: utf-8


__author__ = 'Frederick NEY'

from . import ConfigExceptions
from . import QueryExceptions
from . import RuntimeExceptions
from flask_framework.Deprecation import module_deprecation
module_deprecation(__name__, __name__.lower(), '1.3.0')
from . import ConfigExceptions as config
from . import QueryExceptions as query
from . import RuntimeExceptions as runtime
