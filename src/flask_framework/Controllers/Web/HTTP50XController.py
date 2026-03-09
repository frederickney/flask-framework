# coding: utf-8


__author__ = 'Frederick NEY'

from flask import render_template as template
from flask_framework.Deprecation import module_deprecation
module_deprecation(__name__, 'flask_framework.controllers.web.default.errors.http_50x', '1.3.0')

def error500(error):
    return template('50x.html', title=error)
