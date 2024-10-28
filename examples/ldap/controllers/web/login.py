# coding: utf-8

__author__ = 'Frédérick NEY'


from flask_framework.Server import Process
from flask_framework.Utils.Auth.ldap import login_required, LDAP
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
        return template('login/success.html', user=session.get('username'))