# coding: utf-8
import logging
import os
from logging.handlers import TimedRotatingFileHandler

_level = logging.WARNING


def configure_logs(name, level=_level):
    """
    Setup logging configuration, logging level for name
    :param name:
    :type name: str
    :param level:
    :type level: str
    :type level: int
    :return:
    """

    logger = logging.getLogger(name)
    if isinstance(level, str):
        logger.setLevel(level.upper())
    else:
        logger.setLevel(level)


def configure_basic_logger(level=_level):
    """
    Setup logging base configuration, logging level
    :param level:
    :type level: str
    :type level: int
    """
    logging.getLogger().handlers = []
    logging.basicConfig(
        level=level.upper() if isinstance(level, str) else level,
        format='%(asctime)s %(levelname)s %(message)s',
    )


def setup_file_logging(level=_level):
    """
    Setup logging configuration, logging handler, logging formatting, ...
    :param level:
    :type level: str
    :type level: int
    :return:
    """
    logging.getLogger().handlers = []
    if os.environ.get("LOG_DIR", None):
        os.environ.setdefault("log_dir", os.environ.get("LOG_DIR", "/var/log/server/"))
        os.environ.setdefault("log_file", os.path.join(os.environ.get("log_dir"), 'process.log'))
        if not os.path.exists(os.path.dirname(os.environ.get('log_file'))):
            os.mkdir(os.path.dirname(os.environ.get('log_file')), 0o755)
    if os.environ.get("log_file", None):
        logging.basicConfig(
            level=level.upper() if isinstance(level, str) else level,
            format='%(asctime)s %(levelname)s %(message)s',
            handlers=[
                TimedRotatingFileHandler(
                    filename=os.environ.get('log_file'),
                    when='midnight',
                    backupCount=30
                )
            ]
        )
    else:
        logging.basicConfig(
            level=level.upper() if isinstance(level, str) else level,
            format='%(asctime)s %(levelname)s %(message)s',
        )
    return os.environ.get("log_file", None)
