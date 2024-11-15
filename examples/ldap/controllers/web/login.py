# coding: utf-8

__author__ = 'Frédérick NEY'


from flask_framework.Server import Process
from flask_framework.Utils.Auth.ldap import LDAP
from flask_login import login_required, current_user
from flask import render_template as template


class Controller(object):

    @staticmethod
    def login():
        return LDAP.login()

    @staticmethod
    def logout():
        return LDAP.logout()

    @staticmethod
    @login_required
    def test():
        from flask import session
        return template('login/success.html', user=current_user.mail)