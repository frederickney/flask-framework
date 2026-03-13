# coding: utf-8


__author__ = "Frederick NEY"


# coding: utf-8


__author__ = "Frederick NEY"

import sys
from . import Database as database
from .Database import decorators
from . import Config as config
from . import Deprecation as deprecation
from . import Exceptions as exceptions
from . import Libs as libs
from .Utils import Auth as auth
from . import Utils as utils
from . import Extensions as extensions
from .Exceptions import ConfigExceptions, QueryExceptions, RuntimeExceptions
from . import Server as core

def set_upper_version_module():
    sys.modules["flask_framework.utils"] = utils
    sys.modules["flask_framework.database"] = database
    sys.modules["flask_framework.database.decorators"] = decorators
    sys.modules["flask_framework.deprecation"] = deprecation
    sys.modules["flask_framework.exceptions"] = exceptions
    sys.modules["flask_framework.extensions"] = extensions
    sys.modules["flask_framework.exceptions.config"] = ConfigExceptions
    sys.modules["flask_framework.exceptions.query"] = QueryExceptions
    sys.modules["flask_framework.exceptions.runtime"] = RuntimeExceptions
    sys.modules["flask_framework.libs"] = libs
    sys.modules["flask_framework.utils"] = utils
    sys.modules["flask_framework.utils.auth"] = auth
    sys.modules["flask_framework.core"] = core
    sys.modules["flask_framework.config"] = config