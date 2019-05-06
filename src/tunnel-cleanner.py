# coding: utf-8

__author__ = 'Frederick NEY'

import requests
from Config import Environment
import os

if 'CONFIG_FILE' in os.environ:
    Environment.load(os.environ['CONFIG_FILE'])
else:
    Environment.load("/etc/server/config.json")

request_counter = 0
while True:
    request_counter+=1
    try:
        rsp = requests.get(Environment.SERVER_DATA['URL'])
        print("Request n°%d: code %d" % (request_counter, rsp.status_code))
        if rsp.status_code == 200 or rsp.status_code == 404:
            exit(0)
    except Exception as e:
        print("Request n°%d: %s" % (request_counter, str(e.args)))
    except KeyboardInterrupt:
        exit(0)

