#!/usr/bin/python

import sys
from elasticsearch import Elasticsearch
import ConfigParser
import os
import pycurl
import json
from StringIO import StringIO
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import time

import atexit
import ssl
import re
import hashlib
from lhcp_server_provisioning_function import *

config = read_config('lhcp_server_provisioning.conf')
country = [ 'it','uk']
#country = [ 'it']
for c in country:
    print c
    print cerca_backup(server_farm=c,username=config['general']['lhbk_user'],password=config['general']['lhbk_password'],searchAll=True,verbose=True)
