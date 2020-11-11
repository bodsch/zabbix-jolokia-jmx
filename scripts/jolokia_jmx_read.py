#!/usr/bin/env python3

import urllib.request
from urllib.error import URLError, HTTPError
import json
import sys
# import base64
import argparse
import logging
from enum import Enum


class JolokiaRead(object):
    """
      docstring for JolokiaRead
    """
    class ExitCode(Enum):
        """
          Enum Class to better select ExitCodes
        """
        OK = 0
        WARNING = 1
        CRITICAL = 2
        UNKNOWN = 3

    def __init__(self):
        """

        """
        self.args = {}
        self.parse_args()

        self.host = self.args.hostname
        self.port = self.args.port
        self.username = self.args.username
        self.password = self.args.password
        self.attr = self.args.attr
        self.key = self.args.key

        self.attr = self.attr.replace(' ', '%20')
        self.key = self.key.replace(' ', '%20')

        # argument 1 is the bean
        # argument 2 is the key
        self.url = "http://{}:{}/jolokia/read/{}/{}".format(
            self.host,
            self.port,
            self.attr,
            self.key)

        self.log = logging.getLogger('JolokiaRead')
        streamhandler = logging.StreamHandler(sys.stdout)
        self.log.addHandler(streamhandler)
        self.log.setLevel(logging.INFO)

    def parse_args(self):
        """
          parse commandline parameters
        """
        p = argparse.ArgumentParser(description='Icinga2 slack notification')

        p.add_argument('--hostname', required=True,
                       help="connect to jolokia endpoint")
        p.add_argument('--port', default="8080")
        p.add_argument('--attr', required=True, help="java.lang:type=Memory")
        p.add_argument('--key', required=True, help="HeapMemoryUsage")
        p.add_argument('--username')
        p.add_argument('--password')

        self.args = p.parse_args()

    def check(self):
        """

        """
        status = 404

        if(self.username and self.password):
            password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
            password_mgr.add_password(
              None,
              self.url,
              self.username,
              self.password)
            handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
            proxy_support = urllib.request.ProxyHandler({})

            opener = urllib.request.build_opener(handler, proxy_support)
        else:
            opener = urllib.request.build_opener()

        if(opener):
            try:
                page = opener.open(self.url).read()
            except HTTPError as ex:
                print("Error code: {}".format(ex.code))
                sys.exit(self.ExitCode.CRITICAL.value)
            except URLError as ex:
                print("Error: {}".format(ex.reason))
                sys.exit(self.ExitCode.CRITICAL.value)
            else:
                resp_dict = json.loads(page)

                if(isinstance(resp_dict, dict)):
                    status = resp_dict.get('status')

        # log what happened, this is for testing.
        # Also let Zabbix know that the item sent was not supported.
        if(status != 200):
            print("ZBX_NOTSUPPORTED")
            sys.exit(self.ExitCode.CRITICAL.value)

        print(json.dumps(resp_dict.get('value')))

        sys.exit(self.ExitCode.OK.value)

# -------------------------------------------------------------------------------------------------


jolokia = JolokiaRead()
jolokia.check()
