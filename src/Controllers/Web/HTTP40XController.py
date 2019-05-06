# coding: utf-8

__author__ = 'Frederick NEY'

from flask import render_template as template

def error404(error):
    return template('40x.pyhtml', title=error)
