# coding: utf-8


__author__ = "Frederick NEY"


import os
import ldap

from functools import wraps
from flask import current_app, flash, render_template, session, redirect, url_for
from flask_wtf import FlaskForm
from functools import wraps
from string import capwords
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


FIELDS = (
    'sAMAccountName',
    'distinguishedName',

    'givenName', # 'first_name'
    'sn', # 'last_name',
    'middleName', # 'middle_name',
    'description', # 'full_name',
    'memberOf',

    'company', # 'company',
    'department', # 'department',
    'title', # 'title',
    'manager', # 'manager',

    'cn', # 'name_lat',
    'name', # 'name_lat',
    'displayName', # 'display_name',
    'displayNamePrintable',

    'comment',            # 'gender',
    'primaryTelexNumber', # 'birth_date',

    'employeeID', # 'employee_id',
    'mail', # 'mail',
    'mobile', # 'mobile',
    'streetAddress', # 'location',
    'ipPhone',
    'userPrincipalName',
    'jpegPhoto'
)


def login_required(f):
    """
    Decorator for views that require login.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' in session:
            return f(*args, **kwargs)
        return redirect(url_for(current_app.config['LDAP_LOGIN_VIEW']))
    return decorated


class LDAPForm(FlaskForm):

    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField()


class LDAP(object):
    def __init__(self, app=None):
        self.app = app
        self.login_required = login_required
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('LDAP_HOST', '127.0.0.1')
        app.config.setdefault('LDAP_PORT', 389)
        app.config.setdefault('LDAP_SCHEMA', 'ldap')
        app.config.setdefault('LDAP_DOMAIN', 'example.com')
        app.config.setdefault('LDAP_LOGIN_VIEW', 'login')
        app.config.setdefault('LDAP_SEARCH_BASE', 'OU=Users,DC=example,DC=com')
        app.config.setdefault('LDAP_LOGIN_TEMPLATE', 'login.html')
        app.config.setdefault('LDAP_SUCCESS_REDIRECT', 'index')
        app.config.setdefault('LDAP_PROFILE_KEY', 'sAMAccountName')
        app.config.setdefault('LDAP_AVATAR_LOC', None)
        app.config.setdefault('LDAP_FIELDS', FIELDS)
        # Use the newstyle teardown_appcontext if it's available,
        # otherwise fall back to the request context
        self.login_func = app.config['LDAP_LOGIN_VIEW']

    @staticmethod
    def connect():
        """

        :return: ldap.ldapobject.SimpleLDAPObject
        """
        conn = ldap.initialize('{0}://{1}:{2}'.format(
        current_app.config['LDAP_SCHEMA'],
            current_app.config['LDAP_HOST'],
            current_app.config['LDAP_PORT']))
        return conn


    @staticmethod
    def ldap_query(conn, query):
        """
        Query given AD connection
        :param conn: AD connection
        :type conn : ldap.ldapobject.SimpleLDAPObject
        :param query: string query
        :type query : str
        :return:
        """
        fields = list(current_app.config['LDAP_FIELDS'])
        if fields and not 'sAMAccountName' in fields:
            fields.append('sAMAccountName')
        records = conn.search_s(current_app.config['LDAP_SEARCH_BASE'], ldap.SCOPE_SUBTREE, query, fields)
        conn.unbind_s()
        res = []
        for rec in records:
            if rec[0] is None:
                continue
            newrec = {}
            for field in rec[1].keys():
                try:
                    newrec[field] = rec[1][field][0].decode('utf8') if len(rec[1][field]) == 1 else [value.decode('utf8') for value in rec[1][field]]
                except Exception as e:
                    newrec[field] = None
            res.append(newrec)
        return res

    @staticmethod
    def ldap_login(username, pwd):
        """
        Used to log user using Active Directory.
        This will set the user into flask.session in case of success otherwise will send a flash message
        :param username:
        :type username: str
        :param pwd:
        :type pwd: str
        :return: bool
        """
        try:
            conn = LDAP.connect()
            user = "{0}@{1}".format(username, current_app.config['LDAP_DOMAIN'])
            conn.set_option(ldap.OPT_REFERRALS, 0)
            conn.simple_bind_s(user, pwd.encode('utf8'))
            query = "sAMAccountName=%s" % username
            result = LDAP.ldap_query(conn, query)
            user = result[0] if len(result) >= 1 else None
            if current_app.config['LDAP_REQUIRED_GROUP'] is not None:
                if current_app.config['LDAP_REQUIRED_GROUP'] not in user['memberOf']:
                    flash("Login successful but not authorized.")
                    return False
            session['username'] = username
            session['user'] = user
            return True

        except ldap.LDAPError as e:
            return LDAP.ldap_err(e)
        except Exception as e:
            return LDAP.other_err(e)

    @staticmethod
    def login():
        """
        flask AD login view
        :return:
        """
        ldap_form = LDAPForm()
        if ldap_form.validate_on_submit():
            if LDAP.ldap_login(ldap_form.username.data, ldap_form.password.data):
                return redirect(url_for(current_app.config['LDAP_SUCCESS_REDIRECT']))
            else:
                return render_template(current_app.config['LDAP_LOGIN_TEMPLATE'], form=ldap_form)
        if 'username' in session:
            flash(u"You are already login in {0}".format(session['username']))
            return redirect(url_for(current_app.config['LDAP_SUCCESS_REDIRECT']))
        return render_template(current_app.config['LDAP_LOGIN_TEMPLATE'], form=ldap_form)

    @staticmethod
    def logout():
        """
        flask AD logout view
        :return:
        """
        del session['user']
        del session['username']
        return redirect(url_for(current_app.config['LDAP_LOGIN_VIEW']))

    @staticmethod
    def ldap_err(exc):
        flash(message=exc.args[0]['desc'], category='error')
        return False

    @staticmethod
    def other_err(exc):
        flash(message=exc.message, category='error')
        return False
