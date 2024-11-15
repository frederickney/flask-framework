# coding: utf-8

__author__ = 'Frédérick NEY'

import logging
import saml2
from flask import current_app, redirect, url_for, request
from flask_login import LoginManager
from flask_framework.Server import Process
from flask_login import login_required


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
        cls._lm.user_loader(Process.openid.user)
        cls._openid = Process.openid
        app.add_url_rule('/openid/login/', 'oidc.login', cls.index, methods=['GET'])
        app.add_url_rule('/openid/authorize/', 'oidc.authorize', cls.authorize, methods=['GET'])
        app.add_url_rule('/openid/logout/', 'oidc.logout', cls.logout, methods=['GET'])
        try:
            app.add_url_rule('/logout/', 'logout', cls.logout, methods=['GET'])
            app.add_url_rule('/login/', 'login', cls.index, methods=['GET'])
            Process._csrf.exempt("logout")
        except Exception as e:
            pass

    @classmethod
    def redirect_login(cls):
        return redirect(url_for('oidc.login'))

    @classmethod
    def authorize(cls):
        return cls._openid.authorize()

    @classmethod
    @login_required
    def logout(cls):
        cls._openid.logout()

    @classmethod
    def index(cls):
        return cls._openid.login()
