# coding: utf-8


__author__ = 'Frederick NEY'


import logging


def request(api, uri, method='GET'):
    """
    Execute the http request to the given api
    :param api: object describing web service
    :param uri: endpoint
    :param method: http method
    :return: requests.models.Response
    """

    def inject(func):
        """
        Call the referenced function
        :param func:
        :return:
        """
        def run(*args, **kwargs):
            """
            Run the referenced function
            :param args: function arguments to send through the api
            :param kwargs: function known arguments to send through the api
            :return:
            """
            import requests
            import logging
            params = kwargs.get('uri_parameters', None)
            kwargs = func(*args, **kwargs)
            kwargs.setdefault('method', method)
            kwargs.setdefault('url', "{}/{}".format(api.base_url, uri.format(*params) if params else uri))
            logging.debug(kwargs)
            rsp = requests.request(**kwargs)
            try:
                return rsp.status_code, rsp.json()
            except Exception as e:
                logging.warning(e)
                return rsp.status_code, None

        return run

    return inject

