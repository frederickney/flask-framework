# coding: utf-8


__author__ = 'Frederick NEY'


import flask_framework.Exceptions as Exceptions
import re
import os


__env_matcher = re.compile(r'\$\{([^}^{]+)\}')


def __env_constructor(loader, node):
    ''' Extract the matched value, expand env variable, and replace the match '''
    import logging
    value = node.value
    match = __env_matcher.match(value)
    env_var = match.group()[2:-1]
    try:
        return os.environ.get(env_var) + value[match.end():]
    except TypeError as e:
        logging.warning("Environment not found: {}".format(env_var))
        return "{}".format(value[match.end():])


def _load(file):
    import os.path, yaml
    yaml.add_implicit_resolver('!env', __env_matcher)
    yaml.add_constructor('!env', __env_constructor)
    if isinstance(file, str):
        if os.path.exists(file):
            if os.path.isfile(file):
                try:
                    content = open(file, 'r')
                    try:
                        return yaml.load(content, yaml.FullLoader)
                    except yaml.YAMLError as e:
                        raise Exceptions.ConfigExceptions.InvalidConfigurationFileError(file + ": Invalid YAML format.")
                except Exception as e:
                    raise Exceptions.ConfigExceptions.InvalidConfigurationFileError(file + ": File did not exist.")
            else:
                raise Exceptions.ConfigExceptions.NotAConfigurationFileError(file + ": Not a valid file.")
        else:
            raise Exceptions.ConfigExceptions.NotAConfigurationFileError(file + ": File did not exist.")
    else:
        raise Exceptions.ConfigExceptions.NotAConfigurationFileError("Expected " + type(str) + ", got " + type(file) + ".")
    return


def load(file):
    return _load(file)
