#!/usr/bin/env python3

import urllib.request
import json
import sys
import time
import base64
import argparse
from enum import Enum

class jolokiaDiscovery(object):
    """
      docstring for jolokiaDiscovery
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

        self.attr = self.attr.replace(' ', '%20')

        # argument 1 is the bean
        # argument 2 is the key
        self.url = "http://{}:{}/jolokia/read/{}".format(
            self.host,
            self.port,
            self.attr)

    def parse_args(self):
        """
          parse commandline parameters
        """
        p = argparse.ArgumentParser(description='Icinga2 slack notification')

        p.add_argument('--hostname', required=True,
                       help="connect to jolokia endpoint")
        p.add_argument('--port', default="8080")
        p.add_argument('--attr', required=True, help="java.lang:type=Memory")
        # p.add_argument('--key', required=True, help="HeapMemoryUsage")
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

        data = list()
        line = {}

        print(json.dumps( resp_dict.get('value'), indent = 2 ))

        j = 0
        for jmxobj in resp_dict.get('value').items():

            # jmxobj_dict = jmxobj.split(':')

            print(jmxobj)

            # line["{#JMXOBJ}"] = jmxobj.replace('\"', '%22')
            # line["{#JMXOBJ_BEAN}"] = jmxobj_dict[0]
            #
            # jmxobj_attr = jmxobj_dict[1].split(',')
            #
            # for i in range(len(jmxobj_attr)):
            #     jmxobj_attr_s = jmxobj_attr[i]
            #     attrname = jmxobj_attr_s.split('=')[0]
            #     attrval = jmxobj_attr_s.split('=')[1].replace('\"', '%22')
            #     line['{#JMXOBJ_ATTR_' + attrname.upper() + '}'] = attrval
            #
            # j = j + 1
            #
            # data.append(line.copy())

        print(json.dumps({"data": data}))

        print(resp_dict.get('value'))
        sys.exit(self.ExitCode.OK.value)

# -------------------------------------------------------------------------------------------------


#jolokia = jolokiaDiscovery()
#jolokia.check()


    # verify we have at least two arguments
if len(sys.argv) < 2:
    print("at least two arguments required!")
    exit(1)

attr = sys.argv[1].replace(' ', '%20')
key = sys.argv[2].replace(' ', '%20')

# see if arg3 exists, if not then use 13337 as the default port
try:
    port = sys.argv[3]
except IndexError:
    port = "8080"

# argument 1 is the bean
# argument 2 is the key
url = "http://10.209.6.14:" + port + "/jolokia/read/" + attr + "/" + key

print(url)

if len(sys.argv) >= 5:
    password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, url, sys.argv[4], sys.argv[5])
    handler = urllib.request.HTTPBasicAuthHandler(password_mgr)

    proxy_support = urllib.request.ProxyHandler({})
    opener = urllib.request.build_opener(handler, proxy_support)
else:
    opener = urllib.request.build_opener()

page = opener.open(url).read()

# put in the response dictionary
resp_dict = json.loads(page)

print(json.dumps( resp_dict.get('value'), indent = 2 ))

# log what happened, this is for testing.  Also let Zabbix know that the item sent was not supported.
if resp_dict['status'] != 200:
    print("ZBX_NOTSUPPORTED")
    exit()

data = list()
line = {}


for key, value in resp_dict.get('value').items():
    print(key)
    print(value)

    line["{#JMXOBJ}"] = key.replace('\"', '%22')

    if(isinstance(value, dict)):
        for k,v in value.items():
            print(k)
            print(v)



    else:
        line["{#JMXOBJ_BEAN}"] = value

    print(line)

j = 0
for jmxobj in resp_dict['value']:

    jmxobj_dict = jmxobj.split(':')

    line["{#JMXOBJ}"] = jmxobj.replace('\"', '%22')
    line["{#JMXOBJ_BEAN}"] = jmxobj_dict[0]

    print(line)

    # jmxobj_attr = jmxobj_dict[1].split(',')
    #
    # for i in range(len(jmxobj_attr)):
    #     jmxobj_attr_s = jmxobj_attr[i]
    #     attrname = jmxobj_attr_s.split('=')[0]
    #     attrval = jmxobj_attr_s.split('=')[1].replace('\"', '%22')
    #     line['{#JMXOBJ_ATTR_' + attrname.upper() + '}'] = attrval

    j = j + 1

    data.append(line.copy())

print(json.dumps({"data": data}))
