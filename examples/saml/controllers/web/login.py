# coding: utf-8

__author__ = 'Frédérick NEY'


from flask import render_template as template
from flask_login import login_required, current_user


class Controller(object):

    @staticmethod
    @login_required
    def test():
        from flask import session
        return template('login/success.html', user=current_user.subject)