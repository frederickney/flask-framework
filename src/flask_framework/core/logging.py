# coding: utf-8


import logging


def configure_logs(name, format, output_file, debug='info'):
    """
    Setup logging configuration, logging handler, logging formatting, ...
    :param name:
    :type name: str
    :param format:
    :type format: str
    :param output_file:
    :type output_file: str
    :param debug:
    :type debug: str
    :return:
    """
    logger = logging.getLogger(name)
    formatter = logging.Formatter(format)
    file_handler = logging.FileHandler(output_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logging.getLevelName(debug.upper())
    logger.setLevel(logging.getLevelName(debug.upper()))
