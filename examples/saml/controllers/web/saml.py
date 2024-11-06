# coding: utf-8

__author__ = 'Frédérick NEY'

import logging
import saml2
from flask import current_app, redirect, url_for, request
from flask_login import LoginManager
from flask_framework.Server import Process


class Controller(object):

    @classmethod
    def setup(cls, app, **kwargs):

        """
        :param app:
        :type app: flask.Flask
        :param prefix:
        :type prefix: str
        :param redirect:
        :type redirect: str
        :return:
        """
        cls._lm = LoginManager()
        cls._lm.init_app(app=app)
        cls._lm.unauthorized_handler(cls.redirect_login)
        cls._lm.user_loader(Process.saml.user)
        cls._saml = Process.saml
        app.add_url_rule('/saml/login/', 'saml.login', cls.index, methods=['GET'])
        app.add_url_rule('/saml/metadata/', 'saml.metadata', cls.metadata, methods=['GET'])
        app.add_url_rule('/saml/authorize/', 'saml.authorize', cls.authorize, methods=['POST'])
        app.add_url_rule('/saml/logout/', 'saml.logout', cls.logout, methods=['POST'])
        Process._csrf.exempt("{}.authorize".format(__name__))
        Process._csrf.exempt("{}.login".format(__name__))
        Process._csrf.exempt("{}.logout".format(__name__))
        Process._csrf.exempt("{}.metadata".format(__name__))
        try:
            app.add_url_rule('/logout/', 'logout', cls.logout, methods=['POST'])
            app.add_url_rule('/login/', 'login', cls.index, methods=['GET'])
            Process._csrf.exempt("logout")
        except Exception as e:
            pass

    @classmethod
    def redirect_login(cls):
        return redirect(url_for('saml.login'))

    @classmethod
    def authorize(cls):
        return cls._saml.authorize()

    @classmethod
    def logout(cls):
        cls._saml.saml_logout()

    @classmethod
    def metadata(cls):
        return cls._saml.metadata()

    @classmethod
    def index(cls):
        return cls._saml.saml_login()
