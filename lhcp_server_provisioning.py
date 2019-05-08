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

config = read_config(os.path.dirname(__file__) + '/lhcp_server_provisioning.conf')
#print config

macchine_da_inserire = vmware_getavailableserver(config['general']['host'],config['general']['user'],config['general']['pass'])
check_macchine_da_inserire(macchine_da_inserire,config['general']['min_macchine'],config['general']['verbose'])

for k in config:
    if k != 'general':
        if config['general']['verbose']:
            print "\033[1;36;40mtype " + k + " (user per day: "+ config[k]['user_per_day'] + ")\033[1;37;40m"
        ## prende la lista delle maccchine attive sul provisioning
        active_server=get_active_server(mnt=config[k]['wh'],active='true',tags=config[k]['tags'])
        #print active_server
        ## prende la lista delle macchine disattive sul provisioning
        available_server=get_active_server(mnt=config[k]['wh'],active='false',tags=config[k]['tags'])
        #print available_server
        ## chiede a elasticsearch quali macchine possono entrare nel provisioning
        prov_ssd = valida_macchine(server=available_server,max_user_virtual=config[k]['user_virtual'],max_user_fisica=config[k]['user_fisica'],perc_free=config[k]['disk'],blacklist=config['general']['blacklist'])
        #print prov_ssd
        ## controlla se le macchine attive possono rimanere nel provisioning, in caso negativo mette una nuova macchina nel provisioning e toglie la vecchia
        ## se necessario installa una nuova macchina lhcp
        macchine_da_inserire = controlla_macchine(active_server=active_server,available_server=prov_ssd,config=config[k],macchine_da_inserire=macchine_da_inserire,general_config=config['general'])

check_macchine_da_inserire(macchine_da_inserire,config['general']['min_macchine'],config['general']['verbose'])
