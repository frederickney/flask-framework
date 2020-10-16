#!/usr/bin/python3
# coding: utf-8

__author__ = 'Frederick NEY'

import gevent.monkey

gevent.monkey.patch_all()


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
    import Server
    from Database import Database
    from Config import Environment
    args = args_parser()
    os.environ.setdefault("log_file", os.environ.get("LOG_FILE", "/var/log/server/process.log"))
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format='[%(asctime)s] [%(levelname)s]: %(message)s',
        filename=os.environ.get('log_file')
    )
    logging.info("Starting server...")
    logging.debug("Loading configuration file...")
    if 'CONFIG_FILE' in os.environ:
        Environment.load(os.environ['CONFIG_FILE'])
    else:
        Environment.load("/etc/server/config.json")
    logging.debug("Configuration file loaded...")
    logging.debug("Connecting to default database...")
    Database.register_engines(args.debug)
    Database.init()
    logging.debug("Default database connected...")
    Server.Process.init(tracking_mode=False)
    #Server.Process.init_sheduler()
    logging.debug("Server initialized...")
    logging.debug("Loading server routes...")
    Server.Process.load_routes()
    Server.Process.load_middleware()
    Server.Process.load_socket_events()
    logging.debug("Server routes loaded...")
    #app.teardown_appcontext(Database.save)
    logging.info("Server is now starting...")
    import Extensions
    Extensions.load()
    Server.Process.start(args)


if __name__ == '__main__':
    main()
