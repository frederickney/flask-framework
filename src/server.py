#!/usr/bin/python3
# coding: utf-8

__author__ = 'Frederick NEY'


def args_parser():
    import argparse
    parser = argparse.ArgumentParser(description='Python FLASK server')
    parser.add_argument(
        '-D', '--debug',
        action='store_true',
        help='Activate debug mode'
    )
    parser.add_argument(
        '-p', '--pid',
        action='store_true',
        help='Create pid file'
    )
    parser.add_argument(
        '-la', '--listening_address',
        help='IP address of the server to listen'
    )
    parser.add_argument(
        '-lp', '--listening_port',
        required=True,
        help='Port of the server to listen'
    )
    args = parser.parse_args()
    return args


def main():
    import os, logging
    import Task
    import Server
    from Database import Database
    from Config import Environment
    args = args_parser()
    os.environ.setdefault("log_file", os.environ.get("LOG_FILE", "/var/log/server/process.log"))
    Server.configure_logs('GLOBAL', '[%(asctime)s] [%(levelname)s]: %(message)s', os.environ.get("log_file"), "debug")
    logger = logging.getLogger('GLOBAL')
    logger.info("Starting server...")
    logger.debug("Loading configuration file...")
    if 'CONFIG_FILE' in os.environ:
        Environment.load(os.environ['CONFIG_FILE'])
    else:
        Environment.load("/etc/server/config.json")
    logger.debug("Configuration file loaded...")
    app = Server.Process.init(tracking_mode=False)
    logger.debug("Server initialized...")
    logger.debug("Connecting to default database...")
    if 'default' in Environment.Databases:
        db_conf = Environment.Databases['default']
        Database.setup(
            db_conf['driver'], db_conf['user'], db_conf['password'], db_conf['address'], db_conf['database'], Environment.SERVER_DATA['CAPTURE']
        )
        Database.init()
    logger.debug("Default database connected...")
    logger.debug("Loading server routes...")
    Server.Process.load_routes()
    logger.debug("Server routes loaded...")
    #app.teardown_appcontext(Database.save)
    logger.info("Server is now starting...")
    Server.Process.start(args)


if __name__ == '__main__':
    main()

