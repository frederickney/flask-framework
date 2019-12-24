# coding: utf-8

__author__ = 'Frederick NEY'

from flask import render_template as template
from flask import session

class Controller(object):

    @staticmethod
    def default():
        return template("welcome.jinja2")




