# coding: utf-8

__author__ = 'Frédérick NEY'


from flask_framework.Server import Process
from flask import render_template as template


class Controller(object):

    @staticmethod
    @Process.openid.require_login
    def test():
        from flask import session
        return template('login/success.html', user=session["oidc_auth_profile"].get('email'))