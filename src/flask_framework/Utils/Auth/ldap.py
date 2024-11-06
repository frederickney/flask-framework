# coding: utf-8


__author__ = "Frederick NEY"

import logging

import ldap
from flask import current_app, flash, render_template, session, redirect, url_for, request, g
from flask_login import login_required, logout_user, login_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

from flask_framework.Database import Database

FIELDS = [
    'sAMAccountName',
    'distinguishedName',

    'givenName',  # 'first_name'
    'sn',  # 'last_name',
    'middleName',  # 'middle_name',
    'description',  # 'full_name',
    'memberOf',

    'company',  # 'company',
    'department',  # 'department',
    'title',  # 'title',
    'manager',  # 'manager',

    'cn',  # 'name_lat',
    'name',  # 'name_lat',
    'displayName',  # 'display_name',
    'displayNamePrintable',

    'comment',  # 'gender',
    'primaryTelexNumber',  # 'birth_date',

    'employeeID',  # 'employee_id',
    'mail',  # 'mail',
    'mobile',  # 'mobile',
    'streetAddress',  # 'location',
    'ipPhone',
    'userPrincipalName',
    'jpegPhoto'
]

LDAP_ATTRIBUTE_MAP = {
    'firstname': 'givenName',
    'lastname': 'sn',
    'email': 'mail',
}


class LDAPForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField()


class User(object):
    def __init__(self, attrs):
        for key, attr in attrs.items():
            setattr(self, key, str(attr))

    def get_id(self):
        return getattr(self, 'mail')

    def __repr__(self):
        _str = '{'
        attr = []
        for key in dir(self):
            if not key.startswith('__') and not key.startswith('_') and not key.startswith('set_'):
                attr.append(key)
        for i in range(len(attr)):
            _str += (
                '"{}": "{}"'.format(
                    attr[i],
                    getattr(self, attr[i])
                ) if i == len(attr) - 1
                else '"{}": "{}", '.format(
                    attr[i],
                    getattr(self, attr[i])
                )
            )
        _str += '}'
        return _str

    @property
    def is_active(self):
        return True


class LDAP(object):

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        hosts = app.config.get('LDAP_HOSTS', [])
        app.config.setdefault('LDAP_HOST', hosts[0] if len(hosts) != 0 else '127.0.0.1')
        app.config.setdefault('LDAP_PORT', 389)
        app.config.setdefault('LDAP_SCHEMA', 'ldap')
        app.config.setdefault('LDAP_DOMAIN', 'example.com')
        app.config.setdefault('LDAP_LOGOUT_VIEW', None)
        app.config.setdefault('LDAP_LOGIN_VIEW', 'login')
        app.config.setdefault('LDAP_SEARCH_BASE', 'OU=Users,DC=example,DC=com')
        app.config.setdefault('LDAP_LOGIN_TEMPLATE', 'login.html')
        app.config.setdefault('LDAP_SUCCESS_REDIRECT', 'index')
        app.config.setdefault('LDAP_PROFILE_KEY', 'sAMAccountName')
        app.config.setdefault('LDAP_ATTRIBUTE_MAP', LDAP_ATTRIBUTE_MAP)
        app.config.setdefault('LDAP_AVATAR_LOC', None)
        app.config.setdefault('LDAP_FIELDS', FIELDS)
        app.config.setdefault('LDAP_PROTOCOL_VERSION', 3)
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
        conn.protocol_version = current_app.config.get('LDAP_PROTOCOL_VERSION')
        conn.set_option(ldap.OPT_REFERRALS, 0)
        return conn

    @staticmethod
    def connect_host(server):
        """
        :return: ldap.ldapobject.SimpleLDAPObject
        """
        current_app.config.setdefault('LDAP_HOST', server)
        return LDAP.connect()

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
        if fields and not 'mail' in fields:
            fields.append('mail')
        records = conn.search_s(current_app.config['LDAP_SEARCH_BASE'], ldap.SCOPE_SUBTREE, query, fields)
        res = []
        for rec in records:
            if rec[0] is None:
                continue
        newrec = {}
        for field in rec[1].keys():
            newrec[field] = (
                rec[1][field][0].decode('utf8') if len(rec[1][field]) == 1
                else
                [value.decode('utf8') for value in rec[1][field]]
            )
        res.append(newrec)
        return res

    @staticmethod
    def user_loader(id):
        try:
            from models.persistent import cms
            user = Database.session.query(cms.Users).filter(cms.Users.id == id).first()
            logging.warning("{}: user {}".format(__name__, user))
            if user is None:
                LDAP.logout()
                return user
            user.is_authenticated = True
        except ImportError as e:
            logging.info('{}: with {} flask_cms not installed'.format(__name__, e))
            user = g.user
        return user

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
            for host in current_app.config.get('LDAP_HOSTS'):
                try:
                    conn = LDAP.connect_host(host)
                    conn.simple_bind_s(username, pwd)
                    result = LDAP.ldap_query(conn, "(&(objectClass=user)(mail=" + username + "))")
                    user = None
                    if len(result) > 0:
                        user = User(result[0])
                        try:
                            from models.persistent import cms
                            cms_user = Database.session.query(cms.Users).filter(cms.Users.email == user.mail).first()
                            if cms_user is None:
                                cms_user = cms.Users()
                                for user_attr, ldap_attr in current_app.config.get('LDAP_ATTRIBUTE_MAP').items():
                                    setattr(cms_user, user_attr, getattr(user, ldap_attr))
                                cms_user.is_active = True
                                Database.session.add(cms_user)
                                Database.session.commit()
                            user = cms_user
                        except ImportError as e:
                            logging.info('{}: with {} flask_cms not installed'.format(__name__, e))
                            g.user = user
                            session['user'] = user.__dict__
                            pass
                    conn.unbind_s()
                    return login_user(user)
                except ldap.INVALID_CREDENTIALS as e:
                    return LDAP.ldap_err(e)
                except ldap.LDAPError as e:
                    LDAP.ldap_err(e)
            return False
        except Exception as e:
            return LDAP.other_err(e)

    @staticmethod
    def login(admin_template=None):
        """
        flask AD login view
        :return:
        """
        ldap_form = LDAPForm()
        if ldap_form.validate_on_submit():
            if LDAP.ldap_login(ldap_form.username.data, ldap_form.password.data):
                flash('Logged in successfully.')
                next = request.args.get('next')
                return redirect(
                    next or request.referrer or url_for(current_app.config['LDAP_SUCCESS_REDIRECT']) or url_for('home')
                )

            else:
                return render_template(current_app.config['LDAP_LOGIN_TEMPLATE'], form=ldap_form)
        if current_user.is_authenticated:
            flash(u"You are already login in {0}".format(current_user.email))
            return redirect(url_for(current_app.config['LDAP_SUCCESS_REDIRECT']))
        return render_template(admin_template or current_app.config['LDAP_LOGIN_TEMPLATE'], form=ldap_form)

    @staticmethod
    @login_required
    def logout(admin_template=None):
        """
        flask AD logout view
        :return:
        """
        logout_user()
        flash('logged out')
        return redirect(url_for(admin_template or current_app.config['LDAP_LOGIN_VIEW']))

    @staticmethod
    def ldap_err(exc):
        flash(message=exc.args[0]['desc'], category='error')
        return False

    @staticmethod
    def other_err(exc):
        flash(message=exc, category='error')
        return False
