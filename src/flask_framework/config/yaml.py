# coding: utf-8


__author__ = 'Frederick NEY'

import os
import re

import flask_framework.exceptions as exceptions

__env_matcher = re.compile(r'\$\{([^}^{]+)\}')


def __env_constructor(loader, node):
    """
    Extract the matched value, expand env variable, and replace the match.
    If not found then warning is raised to inform the user that there is missing environ variable.
    :param: loader (Unused here only to make function compatible with pyyaml library)
    :type loader: yaml.Loader
    :param: node of the yaml file
    :type node: yaml.Node
    """
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
    """
    Load yaml file.
    :param file: yaml file.
    :type file: str
    :rtype: dict[str, dict]
    :raise fastapi_framework_mvc.Exceptions.ConfigExceptions.NotAConfigurationFileError:
    if file not exist or if is something else than a file.
    :raise fastapi_framework_mvc.Exceptions.ConfigExceptions.InvalidConfigurationFileError:
    if file is not a valid yaml file.
    """
    import os.path, yaml
    yaml.add_implicit_resolver('!env', __env_matcher)
    yaml.add_constructor('!env', __env_constructor)
    if isinstance(file, str):
        if os.path.exists(file):
            if os.path.isfile(file):
                try:
                    fd = open(file, 'r')
                    try:
                        content = yaml.load(fd, yaml.FullLoader)
                        fd.close()
                        return content
                    except yaml.YAMLError as e:
                        fd.close()
                        raise exceptions.config.InvalidConfigurationFileError(file + ": Invalid YAML format.")
                except Exception as e:
                    raise exceptions.config.InvalidConfigurationFileError(file + ": File did not exist.")
            else:
                raise exceptions.config.NotAConfigurationFileError(file + ": Not a valid file.")
        else:
            raise exceptions.config.NotAConfigurationFileError(file + ": File did not exist.")
    else:
        raise exceptions.config.NotAConfigurationFileError(
            "Expected " + type(str) + ", got " + type(file) + "."
        )
    return


def load(file):
    """
    Load yaml file.
    :param file: yaml file.
    :type file: str
    :rtype: dict[str, dict]
    :raise fastapi_framework_mvc.Exceptions.ConfigExceptions.NotAConfigurationFileError:
    if file not exist or if is something else than a file.
    :raise fastapi_framework_mvc.Exceptions.ConfigExceptions.InvalidConfigurationFileError:
    if file is not a valid yaml file.
    """
    return _load(file)
