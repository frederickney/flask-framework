# coding: utf-8

__author__ = 'Frédérick NEY'


from flask_saml import saml_authenticated
from flask import render_template as template
from flask import current_app
from flask_framework.Server import Process

class Controller(object):

    @staticmethod
    def test():
        from flask import session
        return template('login/success.html', user=session["saml"].get('subject'))