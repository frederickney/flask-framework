# coding: utf-8


__author__ = 'Frederick NEY'

from flask import render_template as template
from flask import request
from flask_framework.Deprecation import module_deprecation
module_deprecation(__name__, 'flask_framework.controllers.web.default.errors.http_40x', '1.3.0')


def page_or_error404(error):
    path = request.path
    if path == '/':
        return template('welcome.html')
    else:
        return template('40x.html', title=error)
