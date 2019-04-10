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

#print serial_update("2018010201")
#print serial_update("2018041001")
#print serial_update("2018041003")
#sys.exit(0)
config = read_config('lhcp_server_provisioning.conf')


## si fa dare da vmware la lista delle macchine da inserire
#macchine_da_inserire = vmware_getavailableserver(config['general']['host'],config['general']['user'],config['general']['pass'])

## inverte le macchine nel provisioning per namesco (per fare la demo)
#if manage_server(server_name="lhcp2020.webapps.net",active='true'):
#    manage_server(server_name="lhcp2046.webapps.net",active='false')

#print config
for k in config:
    if k != 'general':
        print "\033[1;36;40mtipologia " + k + "\033[1;37;40m"
        ## prende la lista delle maccchine attive sul provisioning
        #print "active server"
        active_server=get_active_server(mnt=config[k]['wh'],active='true',tags=config[k]['tags'])
        print valida_macchine(server=active_server,max_user_virtual=config[k]['user_virtual'],max_user_fisica=config[k]['user_fisica'],perc_free=config[k]['disk'])
        #print active_server
        ## prende la lista delle macchine disattive sul provisioning
        available_server=get_active_server(mnt=config[k]['wh'],active='false',tags=config[k]['tags'])
        #print "available server"
        #print available_server
        ## chiede a elasticsearch quali macchine possono entrare nel provisioning
        prov_ssd = valida_macchine(server=available_server,max_user_virtual=config[k]['user_virtual'],max_user_fisica=config[k]['user_fisica'],perc_free=config[k]['disk'])
        print "macchine papabili"
        print prov_ssd
        #if k == "names.co.uk":
        #    controlla_macchine(active_server=active_server,available_server=prov_ssd,config=config[k],macchine_da_inserire=macchine_da_inserire,general_config=config['general'])
