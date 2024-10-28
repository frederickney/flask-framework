# coding: utf-8

__author__ = "Frédérick NEY"

from flask_saml import FlaskSAML as SAML
from flask_saml import login, logout, login_acs, metadata, saml_authenticated, saml_log_out, _session_login, _session_logout

def _get_metadata(metadata_url):  # pragma: no cover
    """

    :param metadata_url:
    :type metadata_url: str
    :return:
    """
    if metadata_url.startswith('http'):
        import requests
        response = requests.get(metadata_url)
        if response.status_code != 200:
            exc = RuntimeError(
                'Unexpected Status Code: {0}'.format(response.status_code))
            exc.response = response
            raise exc
        return response.text
    else:
        import os
        file = open(metadata_url, 'r')
        text = file.read()
        file.close()
        return text


class FlaskSAML(SAML):

    def __init__(self, app=None, debug=False):
        super(FlaskSAML, self).__init__(None, debug)
        self.app = app
        if self.app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('SAML_PREFIX', '/saml')
        app.config.setdefault('SAML_DEFAULT_REDIRECT', '/')
        app.config.setdefault('SAML_USE_SESSIONS', True)

        config = {
            'metadata': _get_metadata(
                metadata_url=app.config['SAML_METADATA_URL'],
            ),
            'prefix': app.config['SAML_PREFIX'],
            'default_redirect': app.config['SAML_DEFAULT_REDIRECT'],
        }

        saml_routes = {
            'logout': logout,
            'sso': login,
            'acs': login_acs,
            'metadata': metadata,
        }
        for route, func in saml_routes.items():
            path = '%s/%s/' % (config['prefix'], route)
            app.add_url_rule(path, view_func=func, methods=['GET', 'POST'])

        # Register configuration on app so we can retrieve it later on
        if not hasattr(app, 'extensions'):  # pragma: no cover
            app.extensions = {}
        app.extensions['saml'] = self, config

        if app.config['SAML_USE_SESSIONS']:
            saml_authenticated.connect(_session_login, app)
            saml_log_out.connect(_session_logout, app)

