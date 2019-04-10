#!/usr/bin/python

import unittest
import sys
from unittest import TestCase

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


class TestStringMethods(unittest.TestCase):
    config = read_config('lhcp_server_provisioning.conf')

    def test_read_config(self, config=config):
        """ si assicura di riuscire a leggere correttamente la configurazione """
        self.assertTrue(config)
        for k in config:
            if k != 'general':
                for v in ['brand', 'user_fisica', 'user_virtual', 'disk', 'user_per_day', 'wh', 'puppet_template',
                          'tags']:
                    self.assertTrue(config[k][v])
            else:
                for v in ['brand', 'host', 'user', 'pass', 'puppet_path', 'puppet_git_path', 'blacklist',
                          'temporary_ipaddr']:
                    self.assertTrue(config[k][v])

    def test_macchine_da_inserire(self, config=config):
        """ controlla che l'array macchine_da_inserire sia popolato (la lista deve essere non vuota) """
        macchine_da_inserire = vmware_getavailableserver(config['general']['host'], config['general']['user'],
                                                         config['general']['pass'])
        self.assertTrue(macchine_da_inserire)

    def test_get_active_server(self, config=config):
        """ controlla le macchine attive per ogni brand """
        for k in config:
            if k != 'general':
                self.assertTrue(get_active_server(mnt=config[k]['wh'], active='true', tags=config[k]['tags']))

    def test_get_available_server(self, config=config):
        """ controlla le macchine disponibili per ogni brand """
        for k in config:
            ## escludo anche amenworl.nl perche' potrebbe non avere macchine disponibili
            if k != 'general' and k != 'amenworld.nl':
                self.assertTrue(get_active_server(mnt=config[k]['wh'], active='false', tags=config[k]['tags']))

    def test_valida_macchine(self, config=config):
        """ controlla la validazione delle macchine solo per il brand principale """
        b = 'register.it'
        available_server = get_active_server(mnt=config['register.it']['wh'], active='false',
                                             tags=config['register.it']['tags'])
        self.assertTrue(valida_macchine(server=available_server, max_user_virtual=config[b]['user_virtual'],
                                        max_user_fisica=config[b]['user_fisica'], perc_free=config[b]['disk'],
                                        blacklist=config['general']['blacklist']))

    def test_check_macchina(self, config=config):
        """ fa un test delle macchine solo per il brand principale """
        #check di una macchina in blacklist
        dic,res = check_macchina(host="lhcp1085.webapps.net",blacklist=['lhcp1085.webapps.net'])
        self.assertFalse(dic)
        self.assertFalse(res)
        #check di un host nullo
        dic,res = check_macchina(host="")
        self.assertFalse(dic)
        self.assertFalse(res)

        b = 'register.it'
        active_server = get_active_server(mnt=config[b]['wh'], active='true', tags=config[b]['tags'])
        for i in range(len(active_server)):
            dic, res = check_macchina(host=active_server[i], max_user_virtual=config[b]['user_virtual'],
                                      max_user_fisica=config[b]['user_fisica'], perc_free=config[b]['disk'])

            for key in dic:
                if (dic[key]['df'] and dic[key]['users'] and dic[key]['disktype'] == "SSD"):
                    self.assertTrue(res)
                else:
                    self.assertFalse(res)

    def test_naemonDowntime(self):
        """ inserisce un downtime per un host per pochi secondi"""
        self.assertTrue(naemonDowntime(vm='lhcp1021.webapps.net',time=10,comment="unittest"))
        #self.assertFalse(naemonDowntime(vm='lhcp0000.webapps.net',time=10,comment="unittest"))

    def test_insert_remove_server_into_provisioning(self):
        """ inserisce un server nel provisioning """
        """ e subito dopo lo toglie """
        server = 'lhcp1021.webapps.net'
        self.assertFalse(check_server(server))
        self.assertTrue(manage_server(server, 'true'))
        self.assertTrue(check_server(server))
        self.assertTrue(manage_server(server, 'false'))
        self.assertFalse(manage_server(server, 'false'))
        self.assertFalse(check_server(server))
        self.assertFalse(check_server(server))

    def test_get_active_server(self,config=config):
        """ check the function """
        self.assertFalse(get_active_server(mnt="",active='true',tags=[]))
        self.assertTrue(get_active_server(mnt="6666", active='true', tags=[]))

    def test_get_ipaddr(self):
        """ test ipaddress function """
        self.assertEqual(get_ipaddr("lhcp0004"),"81.88.62.4")
        self.assertEqual(get_ipaddr("lhcp1004"),"185.2.4.4")
        self.assertEqual(get_ipaddr("lhcp2004"),"185.2.5.4")
        self.assertFalse(get_ipaddr("lhcp0266"))

    def test_get_ipaddr_eth1(self):
        """ test ipaddress function """
        #self.assertEqual(get_ipaddr_eth1("lhcp0004"),"81.88.62.4")
        self.assertEqual(get_ipaddr_eth1("lhcp1004"),"172.22.16.4")
        self.assertEqual(get_ipaddr_eth1("lhcp2004"),"172.22.17.4")
        self.assertFalse(get_ipaddr_eth1("lhcp0266"))

    def test_cerca_backup(self):
        """ cerca macchine di backup disponibili """
        dic=cerca_backup()
        self.assertTrue(dic)

    def test_utenti_residui(self):
        """ cerca utenti residui per macchina """
        """ caso macchina fisica e macchina virtuali con limiti differenti """
        dic = {}
        dic['lhcp2052.webapps.net'] = {'df': 88, 'users': 200, 'virtual': True, 'disktype': 'SSD'}
        dic['lhcp1052.webapps.net'] = {'df': 88, 'users': 200, 'virtual': False, 'disktype': 'SSD'}
        res = utenti_residui(dic=dic,users_default=400,users_virtual=300)
        self.assertTrue(res)
        self.assertEqual(int(res),300)

    def test_serial_update(self):
        """ testa l'aggiornamento del seriale nella configurazione di bind """
        today = str(datetime.datetime.now().strftime('%Y%m%d')) + "01"
        serial = serial_update(today)
        self.assertTrue(serial)
        serial = "2010040401"
        self.assertTrue(serial)

    def test_create_reverse(self,general_config=config['general']):
        """ testa l'aggiornamento della reverse """
        ## macchina che non deve esistere
        res = create_reverse('lhcp2555',general_config['puppet_git_path'])
        self.assertFalse(res)
        ## macchina gia' presente fra le reverse
        res = create_reverse('lhcp2001',general_config['puppet_git_path'])
        self.assertFalse(res)

    def test_configure_naemon(self,puppet_template=config['register.it']['puppet_template'],puppet_path=config['general']['puppet_path']):
        res = configure_naemon('lhcp1021',puppet_template,puppet_path)
        self.assertFalse(res)

    def test_check_macchine_da_inserire(self):
        self.assertTrue(check_macchine_da_inserire(['lhcp1021','lhcp1022','lhcp1023'],2))
        self.assertFalse(check_macchine_da_inserire(['lhcp1021','lhcp1022','lhcp1023'],5))

if __name__ == '__main__':
    unittest.main()

