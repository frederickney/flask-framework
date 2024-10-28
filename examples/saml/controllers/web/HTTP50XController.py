# coding: utf-8


__author__ = 'Frederick NEY'


from flask import render_template as template


def error500(error):
    return template('50x.html', title=error)
