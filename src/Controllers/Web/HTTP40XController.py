# coding: utf-8

__author__ = 'Frederick NEY'

from flask import render_template as template
from flask import request


def page_or_error404(error):
    path = request.path
    if path == '/':
        return template('index.pyhtml')
    else:
        return template('40x.pyhtml', title=error)
