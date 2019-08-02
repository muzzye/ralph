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
from pyproxmox import *

import time
import datetime

import atexit
import ssl
import re
import hashlib
import r1soft

def read_config(file):
    """ legge da un file di configurazione e ritorna un dizionario con le configurazioni """

    # Lettura del file di configurazione
    config = ConfigParser.ConfigParser()
    config.read(file)

    conf = {}
    blacklist = []
    for black in config.get('general','blacklist').split(','):
        blacklist.append(black)
    hyp_sf = []
    for hsf in config.get('general', 'hypervisor_serverfarm').split(','):
        hyp_sf.append(hsf)
    ## TODO: gestire l'errore nel caso in cui manchi un parametro (prevedere un default)
    conf['general'] = { 'hypervisor_serverfarm': hyp_sf, 'brand': config.get('general','brand'), 'puppet_path': config.get('general','puppet_path'), 'puppet_git_path': config.get('general','puppet_git_path'), 'blacklist': blacklist , 'min_macchine': config.get('general','min_macchine'), 'day_warning': config.get('general','day_warning'), 'day_critical': config.get('general','day_critical'), 'dontinstall': config.getboolean('general','dontinstall'), 'verbose': config.getboolean('general','verbose'), 'lhbk_user': config.get('general','lhbk_user'), 'lhbk_password': config.get('general','lhbk_password') }
    for hyp_sf in conf['general']['hypervisor_serverfarm']:
        conf[hyp_sf]= { 'type': config.get(hyp_sf,'type'), 'server_farm': config.get(hyp_sf,'server_farm'), 'host': config.get(hyp_sf,'host'), 'user': config.get(hyp_sf,'user'), 'pass': config.get(hyp_sf,'pass'), 'temporary_ipaddr': config.get(hyp_sf,'temporary_ipaddr') }
    for brand in conf['general']['brand'].split(','):
        conf[brand]= { 'brand': config.get(brand,'brand'), 'user_fisica': config.get(brand,'user_fisica'), 'user_virtual': config.get(brand,'user_virtual'), 'disk': config.get(brand,'disk'), 'user_per_day': config.get(brand,'user_per_day'), 'wh': config.get(brand,'wh'), 'puppet_template': config.get(brand,'puppet_template'), 'tags': config.get(brand,'tags').split(","), 'preferred_serverfarm':config.get(brand,'preferred_serverfarm').split(",") }
    return conf


def check_macchina(host='', max_user_virtual=300,max_user_fisica=800,perc_free=30,blacklist=[]):
    """ data la macchina e il brand ritorna: """
    """ - True se la macchina puo' restare nel provisioning"""
    """ - False altrimenti"""
    """ i parametri per rimanere nel provisioning sono: """
    """ - disco SSD """
    """ - utenti <= max_user (virtual o fisica a seconda della tipologia della macchina) """
    """ - disco libero >= perc_free """
    dic = {}

    if (host == ""):
        return dic,False

    if host in blacklist:
        return dic,False

    max_user = {}
    max_user['virtual'] = max_user_virtual
    max_user['default'] = max_user_fisica

    es = Elasticsearch([{'host': '172.22.131.66', 'port': 9200}])

    request = '{"aggs": {"hostname": {"terms": {"field": "host.name","size": 1000,"order": {"_count": "desc"}},"aggs": {"df": {"terms": {"field": "perc_disk_free","size": 1000,"order": {"_count": "desc"}},"aggs": {"users": {"terms": {"field": "tot_users_real","size": 1000,"order": {"_count": "desc"}},"aggs": {"disktype": {"terms": {"field": "disk_type","size": 5,"order": {"_count": "desc"}},"aggs": {"crtl": {"terms": {"field": "ctrl_type","size": 1000,"order": {"_count": "desc"}}}}}}}}}}}},"size": 0,"version": true,"_source": {"excludes": []},"query": {"bool": {"must": [{"range": {"@timestamp": {"gte": "now-80m","lte": "now"}}},{"match_phrase": {"host.name": {"query": "' + host + '"}}}]}}}'

    #print request
    res = es.search(index="systems-*", body=request )

    #print res ## debug only

    for hit in res['aggregations']['hostname']['buckets']:
        hostname = hit['key']
        df = hit['df']['buckets'][0]['key']
        users = hit['df']['buckets'][0]['users']['buckets'][0]['key']
        disktype =  hit['df']['buckets'][0]['users']['buckets'][0]['disktype']['buckets'][0]['key']
        controller = hit['df']['buckets'][0]['users']['buckets'][0]['disktype']['buckets'][0]['crtl']['buckets'][0]['key']
        if controller == 'VMWare':
            virtual = True
            maxu = max_user['virtual']
            ## le virtuali hanno tutte il disco SSD
            disktype = "SSD"
        else:
            virtual = False
            maxu = max_user['default']
        if not hostname in dic.keys():
            dic[hostname] = { 'df': df, 'users': users, 'disktype': disktype, 'virtual': virtual }
        if int(maxu) >= int(users) and int(df) > int(perc_free):
            if disktype == "SSD":
                return dic,True
        else:
            return dic,False
    return dic,False

def naemonDowntime(vm='',time=900,user='lhcp_autoprovisioning',comment='inserimento_in_produzione'):
    """ mette la macchina vm in downtime """
    URL="https://monitor.dada.eu/pynag/dt/host/add"
    username = "control"
    password = "smammella"

    c = pycurl.Curl()
    c.setopt(c.URL, URL)
    c.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_BASIC)
    c.setopt(pycurl.USERPWD, username + ':' + password)
    #c.setopt(pycurl.HTTPHEADER, ['Content-Type: application/x-www-form-urlencode'])
    p = "h=" + vm + "&u=" + user + "&d=" + str(time) + "&c=" + comment
    #print "post value " + p
    c.setopt(c.POSTFIELDS, p)
    c.setopt(c.VERBOSE, False)
    c.setopt(pycurl.WRITEFUNCTION, lambda x: None)
    try:
        c.perform()
    except:
        return False
    if c.getinfo(pycurl.HTTP_CODE) == 200:
        return True
    return False

def insertServerInProvisioning(vm,wholesalers,tags):
    """ given a server vm put into provisioning in disable state """
    apiURL = 'http://cpanel.dadapro.net:8083/cpanel-adm/instance'

    txt = ""
    for i in range(len(tags)):
        txt += '"' + tags[i] + '",'

    all_tags = "[ " + txt[0:-1] + " ]"
    c = pycurl.Curl()
    c.setopt(c.URL, apiURL)
    c.setopt(pycurl.HTTPHEADER, ['Accept: application/json','Content-Type: application/json','charset=UTF-8'])
    c.setopt(c.POSTFIELDS, '{ "host": "' + vm + '.webapps.net", "active": false, "wholesalers": [ "' + wholesalers + '-EUROMNT" ], "tags": ' + all_tags + ' }')
    c.setopt(c.VERBOSE, False)
    c.perform()

def getVmSwitchedOff(vm, depth=1):
   """ return the list of vmware virtual machine switched off """
   """ (based on ^lhcp\d+$ naming convention """
   maxdepth = 10
   vm_poff_list = []
   # if this is a group it will have children. if it does, recurse into them
   # and then return
   if hasattr(vm, 'childEntity'):
      if depth > maxdepth:
         return
      vmList = vm.childEntity
      for c in vmList:
         name = getVmSwitchedOff(c, depth+1)
         if name:
             vm_poff_list.append(name)
      return vm_poff_list

   # if this is a vApp, it likely contains child VMs
   # (vApps can nest vApps, but it is hardly a common usecase, so ignore that)
   if isinstance(vm, vim.VirtualApp):
      vmList = vm.vm
      for c in vmList:
         getVmSwitchedOff(c, depth + 1)
      return

   summary = vm.summary

   if summary.runtime.powerState == "poweredOff" and re.match("^lhcp\d+$",summary.config.name):
      return summary.config.name

   return

def powerOnProxmox(proxmox,node,vmid):
    """ power on a virtual machine on proxmox """
    proxmox.startVirtualMachine(node,vmid)

def getProxmoxVmSwitchedOff(proxmox,name="^lhcp\d+$"):
    """ given a proxmox connection and a name to be used as pattern """
    """ return the list of poweredoff servers """
    lista = []
    for node in proxmox.getClusterNodeList()['data']:
        for vm in proxmox.getNodeVirtualIndex(node['node'])['data']:
            if vm['status'] == 'stopped' and re.match(name,vm['name']):
                lista.append({'name': vm['name'], 'vmid': vm['vmid'], 'node': node['node']})
    return lista

def get_ipaddr(vm):
    """ data una macchina ritorna l'indirizzo ip"""
    """ se corretto altrimenti ritorna null """
    hnum = re.findall("\d+$",vm)
    if int(hnum[0][1:]) < 255:
        ip4 = str(int(hnum[0][1:4]))
        if int(hnum[0][0]) == 0:
            ## macchina lhcp0xxx (81.88.62.0/25)
            ip1 = "81.88."
            ip3 = str(62 + int(hnum[0][0]))
        elif int(hnum[0][0]) == 1 or int(hnum[0][0]) == 2:
            ## macchina lhcp[12]xxx (185.2.5.0/21)
            ip1 = "185.2."
            ip3 = str(3 + int(hnum[0][0]))
        elif int(hnum[0][0]) == 3:
            ## macchina lhcp3xxx (81.88.52.0/24)
            ip1 = "81.88."
            ip3 = "52"
        else:
            return False
        ipaddr = ip1 + ip3 + "." + ip4
        return ipaddr
    else:
        return False

def get_ipaddr_eth1(vm):
    """ data una macchina ritorna l'indirizzo ip della eth1"""
    hnum = re.findall("\d+$",vm)
    if int(hnum[0][1:]) < 255:
        if int(hnum[0][0]) == 1 or int(hnum[0][0]) == 2:
            ## macchine lhcp[12]xxx
            ip4 = str(int(hnum[0][1:4]))
            ip1 = "172.22."
            ip3 = str(15 + int(hnum[0][0]))
        elif int(hnum[0][0]) == 3:
            ## macchine lhcp3xxx (172.21.24.0/21)
            ip4 = str(int(hnum[0][1:4]))
            ip1 = "172.21."
            ip3 = str(21 + int(hnum[0][0]))
        else:
            return False
        ipaddr = ip1 + ip3 + "." + ip4
        return ipaddr
    else:
        return False

def validate_r1soft_instance(host='',username='',password='',device='',verbose=False):
    """ given an lhbk server and a device: """
    """ - grab from r1soft all the lhcp that use the device """
    """ - grab from elastic search total disk of the device """
    """ - grab from elastic search total disk of each lhcp """
    """ and return True if r1soft instance can accept more backup """
    somma = 0
    disk_lhbk = get_lhbk_disk(host=host,device=device)
    if verbose == True:
        print host + " " + device + " " + str(disk_lhbk)
    for lhcp in list_lhcp_on_lhbk(lhbk=host,username=username,password=password,device=device):
        value = get_lhcp_disk(lhcp=lhcp)
        if verbose == True:
            print "  " + lhcp + " " + str(value)
        somma = somma + get_lhcp_disk(lhcp=lhcp)
    if verbose == True:
        print "SOMMA: " + str(somma)
    if ( somma * 1.36 ) < disk_lhbk:
        return True
    else:
        return False

def get_lhbk_disk(host='',device=''):
    """ given an lhcp instance and a device return the total disk for the device"""
    es = Elasticsearch([{'host': '172.22.131.66', 'port': 9200}])

    request = '{ "size": 1, "sort": [ { "@timestamp": { "order": "desc", "unmapped_type": "boolean" } } ], "_source": ["beat.hostname","device","total_disk"], "query": { "bool": { "must": [ { "match_all": {} }, { "match_phrase": { "beat.hostname": { "query": "' + host + '" } } }, { "regexp": { "mount": { "value": ".*' + device + '.*" } } }, { "range": {"@timestamp": {"gte": "now-240m","lte": "now"} } } ] } } }'
    #print request
    res = es.search(index="lhbk-*", body=request )
    #for hit in res['hits']['hits']:
    #    print hit['_source']['total_disk']
    try:
        return int(res['hits']['hits'][0]['_source']['total_disk'])*1024
    except:
        return 0

def get_lhcp_disk(lhcp=""):
    """ given an lhcp return the total disk """
    es = Elasticsearch([{'host': '172.22.131.66', 'port': 9200}])

    request = '{ "size": 1, "sort": [ { "@timestamp": { "order": "desc", "unmapped_type": "boolean" } } ], "_source": ["beat.hostname","tot_disk_size"], "query": { "bool": { "must": [ { "match_all": {} }, { "match_phrase": { "beat.hostname": { "query": "' + lhcp + '" } } }, { "range": {"@timestamp": {"gte": "now-240m","lte": "now"} } } ] } } }'

    res = es.search(index="systems-*", body=request )
    #for hit in res['hits']['hits']:
    #    print hit['_source']['total_disk']
    try:
        return int(res['hits']['hits'][0]['_source']['tot_disk_size'])
    except:
        return 0

def list_lhcp_on_lhbk(lhbk="",username="",password="",device=""):
    lhcp = []
    client = r1soft.cdp3.CDP3Client(lhbk, username, password)
    disk_safes = client.DiskSafe.service.getDiskSafes()
    #for ds in disk_safes:
        #print ds['agentID']
        #print ds['path'].split("/")[2]
        #print ds['description']
        #print ds
    for agent in client.Agent.service.getAgents():
        for ds in disk_safes:
            #print ds['path'].split("/")[2]
            #print agent['id']
            #print ds['agentID']
            if ds['path'].split("/")[2] == device and agent['id'] == ds['agentID']:
                lhcp.append(agent.hostname)
    return lhcp

def cerca_backup(server_farm="uk",username='',password='',verbose=False,searchAll=False):
    """ cerca la macchina lhbk e il device con meno risorse in termine di: """
    """ - numero lhcp che fanno backup sul device; - spazio libero sul device. """
    """ restituisce un dizionario contenente device, host, perc_used_disk, num_lhcp: """
    """ {'device': u'sdb', 'host': u'lhbk2002.webapps.net', 'perc_used_disk': 1, 'num_lhcp': 0} """

    if server_farm == "uk":
        lhbk_regexp = 'lhbk[12].*'
    elif server_farm == "it":
        lhbk_regexp = 'lhbk3.*'
    else:
        print "server_farm not set use default server farm (it)"
        lhbk_regexp = 'lhbk3.*'

    es = Elasticsearch([{'host': '172.22.131.66', 'port': 9200}])

    request = '{ "sort": [ { "perc_used_disk": { "order": "asc" } }, { "num_lhcp": { "order": "asc" } } ],"_source": ["beat.hostname","device","num_lhcp","perc_used_disk"],  "query": {"bool": { "must": [ { "query_string": { "query": "perc_used_disk: [ 0 TO 60 ] AND num_lhcp: [ 0 TO 10] AND beat.hostname:/' + lhbk_regexp + '/",   "analyze_wildcard": true, "default_field": "*" }},{"range": {"@timestamp": {"gte": "now-140m","lte": "now"}}}]}}}'

    #print request
    res = es.search(index="lhbk-*", body=request )

    #print res['hits']['hits'] ## debug only
    arr=[]
    for hit in res['hits']['hits']:
        #print hit['_source']
        # {u'beat': {u'hostname': u'lhbk1022.webapps.net'}, u'device': u'/dev/sdb1', u'perc_used_disk': u'1', u'num_lhcp': u'0'}
        host = hit['_source']['beat']['hostname']
        device = hit['_source']['device']
        device = re.match(r"^\/dev\/(.*)[1-9]", device).group(1)
        num_lhcp = hit['_source']['num_lhcp']
        perc_used_disk = hit['_source']['perc_used_disk']
        if validate_r1soft_instance(host=host,username=username,password=password,device=device,verbose=verbose):
           arr.append ({ 'host': host, 'device': device, 'num_lhcp': num_lhcp, 'perc_used_disk': perc_used_disk })

    if searchAll:
        return arr

    if len(arr) > 0:
        return arr.pop(0)
    return []

def valida_macchine(server=[],max_user_virtual=300,max_user_fisica=800,perc_free=30,blacklist=[]):
    """ data una lista di macchine con i relativi parametri (max_user,perc_free) """
    """ ritorna un dizionario con le sole macchine papabili per il provisioning come chiave """
    """ e i seguenti valori {'df': 25, 'users': 637, 'virtual': False, 'disktype': u'SSD'} """

    prov_ssd = {}
    for macchina in server:
        if not macchina in blacklist:
            tmp_ssd = {}
            tmp_ssd,res = check_macchina(macchina,max_user_virtual,max_user_fisica,perc_free,blacklist)
            if res:
                prov_ssd.update(tmp_ssd)

    return prov_ssd

def utenti_residui(dic={},users_default=0,users_virtual=0):
    """ dato un dizionario di macchine ritorna il numero di utenti ancora disponibili """
    utenti = 0
    max_user = {}
    max_user['virtual'] = users_virtual
    max_user['default'] = users_default

    for key in dic:
        if dic[key]['virtual']:
            utenti = utenti + int(max_user['virtual']) - int(dic[key]['users'])
        else:
            utenti = utenti + int(max_user['default']) - int(dic[key]['users'])

    return utenti

def serial_update(serial):
    """ return the updated bind serial number """
    today_serial = datetime.datetime.now().strftime('%Y%m%d')
    serial_date = serial[:-2]
    serial_id = serial[8:]
    updated_serial = ''
    if today_serial == serial_date:
        updated_serial = '\t\t\t\t\t%s%02i\t; serial YYYYMMDDnn\n' %\
                         (serial_date, int(serial_id) + 1)
    else:
        updated_serial = '\t\t\t\t\t%s01\t; serial YYYYMMDDnn\n' %\
                         today_serial
    return updated_serial

def create_reverse(server,puppet_git_path):
    """given a server insert a reverse"""
    """if not already present         """
    ip_addr = get_ipaddr(server)
    if ip_addr:
        ip1 = ip_addr.split('.')[0]
        ip2 = ip_addr.split('.')[1]
        ip3 = ip_addr.split('.')[2]
        ip4 = ip_addr.split('.')[3]
        relative_zone_file = "modules/dadabind9/files/zones/db." + str(ip3) + "." + str(ip2) + "." + str(ip1) + ".in-addr.arpa"
        zone_file = puppet_git_path + "/" + relative_zone_file
        #print "ip1: " + str(ip1) + " ip2: " + str(ip2) + " ip3: " + str(ip3) + " ip4: " + ip4 + " file: " + zone_file
        if os.path.isfile(zone_file):
            if not server in open(zone_file).read():
                with open(zone_file, 'r+') as zone:
                    updated_zone = zone.readlines()
                    zone.seek(0)
                    for record in updated_zone:
                        if '; serial' in record:
                            serial = record.split(';')[0].strip()
                            record = serial_update(serial)
                        zone.write(record)
                    zone.write(str(ip4) + "\t\t\tIN\tPTR\t" + str(server) + ".webapps.net.\n")
                    zone.truncate()
                    bashCommand = "cd " + puppet_git_path + " && git pull && git add " + relative_zone_file + " && git commit -m 'autocommit reverse for " + str(server) + "' && git push >/dev/null"
                    #print bashCommand
                    os.system(bashCommand)
                return True
            else:
                print "server " + str(server) + " already present in zone file " + str(zone_file)
                return False
    else:
        return False

def check_server (host):
    """data una macchina ritorna True se e' attiva nel provisioning, False se non lo e'"""
    buffer = StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, 'http://wh-cpanel.it.dadainternal:8083/cpanel-adm/instance?host=' + host)
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()
    body = buffer.getvalue()
    #print body
    #{"host":"lhcp1081.webapps.net","active":true,"wholesalers":["6666-EUROMNT"],"tags":["ssd","reseller"]}
    try:
        return json.loads(body)['active']
    except:
        return False

def manage_server(server_name,active='true'):
    """given a server activate/disactivate the instance in cpanel dns"""
    c = pycurl.Curl()
    c.setopt(pycurl.URL, "http://cpanel.dadapro.net:8083/cpanel-adm/instance?host=" + server_name + "&active=" + active)
    c.setopt(pycurl.HTTPHEADER, ['Accept: application/json','Content-Type: application/json','charset=UTF-8'])
    c.setopt(pycurl.CUSTOMREQUEST, "PUT")
    #c.setopt(pycurl.VERBOSE, 1)
    c.perform()
    if c.getinfo(pycurl.RESPONSE_CODE) == 200:
        return True
    else:
        return False

def get_active_server (mnt="",active='true',tags=[]):
    """ dati un manteiner lo stato della macchina (active=true|false) e un array con i tags """
    """ ritorna un array con la lista delle macchine con lo stato passato come argomento sul provisioning """

    if mnt == "":
        return False
    buffer = StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, 'http://wh-cpanel.it.dadainternal:8083/cpanel-adm/instance?wholesaler=' + mnt + '-EUROMNT&active=' + active + '&tags=' + "%2C".join(tags))

    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()
    body = buffer.getvalue()
    #print body
    #[{"host":"lhcp2011.webapps.net","active":true,"wholesalers":["AMENNL-EUROMNT"],"tags":["ssd","reseller"]}]
    arr = []
    for i in range(len(json.loads(body))):
        arr.append(json.loads(body)[i]['host'])
    return arr

def configure_puppet(vm,puppet_path):
    """ data una macchina la inserisce nel file autosign di puppet """
    ## autosign
    if os.path.isdir(puppet_path):
        f = "autosign.conf"

        bashCommand = "cd " + puppet_path + " && svn up >/dev/null"
        os.system(bashCommand)

        if vm + ".webapps.net" in open(puppet_path + "/" + f).read():
            print "macchina " + vm + " gia' presente nell'autosign di puppet"
        else:
          f = open(puppet_path + "/" + f,"a")
          f.write("\n" + vm + ".webapps.net\n")
          f.close()

          bashCommand = "cd " + puppet_path + " && svn ci -m 'autoadd " + vm + " to autosign' >/dev/null"
          os.system(bashCommand)

        print "puppet run"
        ipaddr = get_ipaddr(vm)
        if ipaddr:
            ## cloudlinux license
            bashCommand = "ssh -i chiave_lhcp_provisioning -oStrictHostKeyChecking=no -p 25088 root@" + ipaddr + " 'rm -rf /var/lve/lveinfo.ver && /usr/sbin/clnreg_ks --force && cagefsctl --reinit > /dev/null'"
            while os.system(bashCommand):
                time.sleep(1)
            bashCommand = "ssh -i chiave_lhcp_provisioning -oStrictHostKeyChecking=no -p 25088 root@" + ipaddr + " 'puppet agent -t >/dev/null; /usr/local/cpanel/3rdparty/bin/php /usr/local/cpanel/whostmgr/docroot/cgi/softaculous/cli.php  --install --cpuser=nagioscheck --cppass=Nagios.User,69 --soft=26 --softdirectory=wp --admin_username=admin --admin_pass=Nagios.User,69 --site_name=\"NagiosCheck Blog\" ; /usr/local/scripts/kibana_systems' >/dev/null 2>&1"
            while os.system(bashCommand):
                time.sleep(1)
            return True
    return False

def configure_naemon(vm,puppet_template,puppet_path,server_farm="uk"):
    """ data una macchina e il relativo template da utilizzare configura puppet """
    """ prende come variabile di input anche il path dove sta la configurazione di puppet """
    """ controlla che il path dove sta la configurazione sia corretto e che la macchina """
    """ non sia gia' sotto puppet """

    if server_farm == "uk":
        filename = "uk_cpanel_hosts.cfg"
        template = "lhcp-virtual"
    elif server_farm == "it":
        filename = "cpanel_cluster_hosts.cfg"
        template = "lhcp-proxmox"
    else:
        print "server farm not recognize: use it as default"
        filename = "cpanel_cluster_hosts.cfg"

    if os.path.isdir(puppet_path):
        p = puppet_path + "/modules/naemon/files/naemon/conf.d_register/puwebhosting/"
        conffile = p + filename
        bashCommand = "cd " + p + " && svn up >/dev/null"
        os.system(bashCommand)

        ## controllo che la macchina non sia gia' sotto puppet
        if vm in open(conffile).read():
            print "macchina " + vm + " gia' presente su puppet"
            return False
        else:
            f = open(conffile,"a")

            f.write("define host {\n")
            f.write("    host_name       " + vm + ".webapps.net\n")
            f.write("    _SHORTNAME      " + vm + "\n")
            f.write("     address        " + vm + ".webapps.net\n")
            f.write("     use            " + template + "," + puppet_template + "\n")
            f.write("}\n")
            f.close()

            bashCommand = "cd " + p + " && svn ci -m 'autoadd " + vm + " to puppet' >/dev/null"
            os.system(bashCommand)
            time.sleep(5)

            bashCommand = "ssh root@anael01.it.dadainternal 'puppet agent -t >/dev/null'"
            os.system(bashCommand)
            return True

def configure_server(vm='',temporary_ipaddr='185.2.6.241',lhbk_user='',lhbk_password='',server_farm='uk'):
    """ data una macchina la configura """
    ipaddr1 = get_ipaddr(vm)
    ipaddr2 = get_ipaddr_eth1(vm)
    if ( ipaddr1 and ipaddr2):
        with open('auto_install.sh', 'r') as file:
            filedata = file.read()

        dic = cerca_backup(server_farm=server_farm,username=lhbk_user,password=lhbk_password,verbose=True)
        # Replace the target string
        filedata = filedata.replace('FAKEHOSTNAME', vm + '.webapps.net')
        filedata = filedata.replace('FAKEIPADDR1', ipaddr1)
        filedata = filedata.replace('FAKEIPADDR2', ipaddr2)
        filedata = filedata.replace('FAKEBACKUPSERVER', dic['host'])
        filedata = filedata.replace('FAKEHOUR', str(dic['num_lhcp']).zfill(2))
        filedata = filedata.replace('FAKEVOLUME', dic['device'])

        # Write the file out again
        with open('auto_install2.sh', 'w') as file:
            file.write(filedata)

        ## copia i files sulla macchina (dovrebbero essere sul template)
        bashCommand = "scp -i chiave_lhcp_provisioning -P 25088 auto_install2.sh root@" + temporary_ipaddr + ":/root/auto_install.sh #>/dev/null 2>&1"
        while os.system(bashCommand):
            print "server not ready, sleep 1 second"
            time.sleep(1)

        bashCommand = "ssh -i chiave_lhcp_provisioning -oStrictHostKeyChecking=no -p 25088 root@" + temporary_ipaddr + " 'chmod +x /root/auto_install.sh' >/dev/null 2>&1"
        while os.system(bashCommand):
            print "server not ready, sleep 1 second"
            time.sleep(1)

        bashCommand = "scp -i chiave_lhcp_provisioning -P 25088 cdp-add-agent.py root@" + temporary_ipaddr + ":/usr/local/scripts/ >/dev/null 2>&1"
        while os.system(bashCommand):
            print "server not ready, sleep 1 second"
            time.sleep(1)

        bashCommand = "scp -i chiave_lhcp_provisioning -P 25088 estrai_cPanel_id.py root@" + temporary_ipaddr + ":/usr/local/scripts/ >/dev/null 2>&1"
        while os.system(bashCommand):
            print "server not ready, sleep 1 second"
            time.sleep(1)

        bashCommand = "ssh -i chiave_lhcp_provisioning -oStrictHostKeyChecking=no -p 25088 root@" + temporary_ipaddr + " '/root/auto_install.sh' #>/dev/null 2>&1"
        while os.system(bashCommand):
            print "server not ready, sleep 1 second"
            time.sleep(1)


        bashCommand = "ssh -i chiave_lhcp_provisioning -oStrictHostKeyChecking=no -p 25088 root@" + temporary_ipaddr + " 'reboot' #> /dev/null 2>&1"
        while os.system(bashCommand):
            print "server not ready, sleep 1 second"
            time.sleep(1)

        return True
    else:
        return False

def softaculous_licence(vm):
    """ data una macchina attiva la licenza softaculous """
    ipaddr = get_ipaddr(vm)
    if ipaddr:

        with open('soft.php', 'r') as file:
            filedata = file.read()

        # Replace the target string
        filedata = filedata.replace('FAKEIPADDR', ipaddr)

        # Write the file out again
        with open('soft2.php', 'w') as file:
            file.write(filedata)

        bashCommand = "php ./soft2.php"
        os.system(bashCommand)

        bashCommand = "ssh -i chiave_lhcp_provisioning -oStrictHostKeyChecking=no -p 25088 root@" + ipaddr + " '/usr/local/cpanel/3rdparty/bin/php /usr/local/cpanel/whostmgr/docroot/cgi/softaculous/cron.php && /usr/local/cpanel/3rdparty/bin/php /usr/local/cpanel/whostmgr/docroot/cgi/softaculous/cli.php -l && mkdir /var/softtmp && chmod 0777 /var/softtmp' >/dev/null 2>&1"
        os.system(bashCommand)
        return True
    else:
        return False

def activate_cloudlinux_license(vm):
    """ dato un indirizzo ip attiva le licenze di cloudlinux """
    ipaddr = get_ipaddr(vm)
    if ipaddr:
        ts = int(time.time())
        key = 'CCqHtuQDnjifqvZW'
        CS = 'register-it-prod'
        m = hashlib.sha1(key+str(ts))
        TOKEN = CS + "|" + str(ts) + "|" + m.hexdigest()

        buffer = StringIO()
        type = [ 1, 16]

        for t in type:
            c = pycurl.Curl()
            c.setopt(c.URL, 'https://cln.cloudlinux.com/api/ipl/register.json?ip=' + ipaddr + '&type=' + str(t) + '&token=' + TOKEN)
            c.setopt(c.WRITEDATA, buffer)
            c.perform()
            c.close()
        return True
    else:
        return False

def create_dns_record(vm):
    """ data una macchina crea i record dns necessari"""
    ipaddr = get_ipaddr(vm)
    if ipaddr:
        bashCommand = "ssh root@git01.it.dadainternal /root/daniele/add_lhcp.pl " + vm + ".webapps.net " + ipaddr
        os.system(bashCommand)
        return True
    else:
        return False

def vmware_connect(host,user,pwd,port=443):
    context = None
    if hasattr(ssl, '_create_unverified_context'):
      context = ssl._create_unverified_context()

    si = SmartConnect(host=host,
      user=user,
      pwd=pwd,
      port=port,
      sslContext=context)

    macchine_da_inserire = []

    if not si:
        print("Could not connect to the specified host using specified username and password")
    else:
         atexit.register(Disconnect, si)

    content = si.RetrieveContent()
    return content

def vmware_poweron(vmnames,content):
    """ accende la macchine server """

    objView = content.viewManager.CreateContainerView(content.rootFolder,
      [vim.VirtualMachine],True)
    vmList = objView.view
    objView.Destroy()

    # Find the vm and power it on
    tasks = [vm.PowerOn() for vm in vmList if vm.name == vmnames]


def getAvailableServer(hyp_type='vmware',host="",user="",passwd="",server_farm='uk',temporary_ipaddr=''):
    """ based on hypervisor return a list of dictionary with available servers """

    if hyp_type == 'vmware':
        lista = vmware_getavailableserver(host,user,passwd,server_farm=server_farm,temporary_ipaddr=temporary_ipaddr)
    elif hyp_type == 'proxmox':
        lista =proxmox_getavailableserver(host,user,passwd,server_farm=server_farm,temporary_ipaddr=temporary_ipaddr)
    else:
        print "hypervisor unknown"
        return False
    return lista

def proxmox_getavailableserver(host,user,pwd,port=8006,server_farm="it",temporary_ipaddr=''):
    """ get from proxmox a list of all virtual servers """
    """ to be switched on """

    a = prox_auth(host,user,pwd)
    b = pyproxmox(a)

    macchine_da_inserire = []
    server = getProxmoxVmSwitchedOff(b)
    for n in server:
        macchine_da_inserire.append({'name': n['name'], 'host': host, 'node': n['node'], 'vmid': n['vmid'], 'type': 'proxmox', 'server_farm': server_farm, 'temporary_ipaddr': temporary_ipaddr, 'user': user, 'pass': pwd})
    macchine_da_inserire.sort()
    return macchine_da_inserire

def vmware_getavailableserver(host,user,pwd,port=443,server_farm="uk",temporary_ipaddr=''):
    """ si collega all'host vmware e ritorna una """
    """ lista di macchine da accendere su vmware """

    macchine_da_inserire = []
    content = vmware_connect(host,user,pwd)

    for child in content.rootFolder.childEntity:
        if hasattr(child, 'vmFolder'):
            datacenter = child
            vmFolder = datacenter.vmFolder
            vmList = vmFolder.childEntity

            for vm in vmList:
                name=getVmSwitchedOff(vm)
                if name:
                    ## if name came in list extract it
                    if isinstance(name, list):
                        for n in name:
                            macchine_da_inserire.append({'name': n, 'host': host, 'type': 'vmware', 'server_farm': server_farm, 'temporary_ipaddr': temporary_ipaddr, 'user': user, 'pass': pwd, 'vmid': '0', 'node': host})
                    else:
                      macchine_da_inserire.append({'name': name, 'host': host, 'type': 'vmware', 'server_farm': server_farm, 'temporary_ipaddr': temporary_ipaddr, 'user': user, 'pass': pwd, 'vmid': '0', 'node': host})
    macchine_da_inserire.sort()
    #macchine_da_inserire.reverse()
    return macchine_da_inserire

def check_macchine_da_inserire(macchine,min_macchine,verbose=True):
    """ controlla se le macchine da inserire siano inferiori al valore nella configurazione"""
    tot_macchine = ""
    for n in macchine:
        tot_macchine = tot_macchine + " " + str(n['name'])

    if len(macchine) < int(min_macchine):
        print "\033[1;31;40mCRITICAL only " + str(len(macchine)) + " servers to be inserted (" + tot_macchine + "), open a task to ct-infra in order to create new servers\033[1;37;40m"
        return False
    else:
        if verbose:
            print str(len(macchine)) + " servers to be inserted:" + tot_macchine
        return True

def poweron_server(hyp_type='vmware',host='',user='',passwd='',server='',node='', vmid=''):
    """ poweron server on every supported hypervisor """
    if hyp_type == 'vmware':
        content=vmware_connect(host,user,passwd)
        vmware_poweron(server,content)
    elif hyp_type == 'proxmox':
        a = prox_auth(host,user,passwd)
        proxmox = pyproxmox(a)
        powerOnProxmox(proxmox,node,vmid)
        ha = []
        ha.append(('sid',"vm:"+vmid))
        ha.append(('max_relocate',"2"))
        ha.append(('max_restart',"2"))
        ha.append(('comment',server))
        ## non si riesce a configurare l'HA perche' l'utente non ha permessi sufficienti
        proxmox.createHaResource(ha)
    else:
        print "type della macchina non riconosciuta, non riesco ad accenderla"
        sys.exit(2)
    return True

def install_new_server(macchina_da_inserire=[],general_config=[],config=[]):
    """ given: """
    """ - an array with the informartion of the server to be installed """
    """ - an array with the general_config """
    """ - an array with the config specific for brand """
    """ Install the server and add to the provisioning """
    print "add a server into provisioning (" + macchina_da_inserire['name'] + ")"
    print "poweron server"
    #print macchina_da_inserire
    poweron_server(hyp_type=macchina_da_inserire['type'],host=macchina_da_inserire['host'],user=macchina_da_inserire['user'],passwd=macchina_da_inserire['pass'],server=macchina_da_inserire['name'],node=macchina_da_inserire['node'],vmid=macchina_da_inserire['vmid'])
    print "activate cloudlinux license"
    activate_cloudlinux_license(macchina_da_inserire['name'])
    print "create DNS records"
    create_dns_record(macchina_da_inserire['name'])
    create_reverse(macchina_da_inserire['name'],general_config['puppet_git_path'])
    print "sleep 60 seconds (waiting for server poweron)"
    time.sleep(60)
    print "configure new server"
    configure_server(vm=macchina_da_inserire['name'],temporary_ipaddr=macchina_da_inserire['temporary_ipaddr'],lhbk_user=general_config['lhbk_user'],lhbk_password=general_config['lhbk_password'],server_farm=macchina_da_inserire['server_farm'])
    print "sleep 60 seconds (waiting for server reboot)"
    time.sleep(60)
    print "activate Softaculous license and update Softaculous"
    softaculous_licence(macchina_da_inserire['name'])
    print "configure puppet"
    configure_puppet(macchina_da_inserire['name'],general_config['puppet_path'])
    print "put server on naemon"
    configure_naemon(macchina_da_inserire['name'],config['puppet_template'],general_config['puppet_path'],server_farm=macchina_da_inserire['server_farm'])
    print "sleep 30 seconds"
    time.sleep(30)
    print "set naemon downtime"
    naemonDowntime(vm=macchina_da_inserire['name'])
    print "insert server into provisioning"
    insertServerInProvisioning(macchina_da_inserire['name'],config['wh'],config['tags'])

def controlla_macchine(active_server=[],available_server=[],config=[],macchine_da_inserire={},general_config=[]):
    """ date 2 liste: """
    """ - active_server: le macchine attive sul provisioning """
    """ - available_server: le macchine disponibili """
    """ controlla se fra gli active_server qualcuno ha raggiunto i limiti """
    """ in caso affermativo prima inserisce una nuova macchina nel provisioning """
    """ e, se e solo se la nuova macchina e' stata aggiunta nel provisioning """
    """ provvede a rimuovere la vecchia macchina nel provisioning """
    """ ritorna un array contenente le macchine ancora da inserire nel provisioning """

    tot_user = 0

    ## per ogni macchina attiva nel provisioning
    for i in range(len(active_server)):
        ## controlla che possa rimanere ancora nel provisioning
        dic,res=check_macchina(host=active_server[i],max_user_virtual=config['user_virtual'],max_user_fisica=config['user_fisica'],perc_free=config['disk'],blacklist=general_config['blacklist'])

        #print available_server
        #print dic
        #print res

        if res:
            ## se la macchina puo' rimanere nel provisioninig stampa tutto ok e comunica quanti utenti e quanto spazio disco ha la macchina
            if general_config['verbose']:
                print active_server[i] + " ok, disk free " + str(dic[active_server[i]]['df']) + "%, users: " + str(dic[active_server[i]]['users']) + " (disk type " + str(dic[active_server[i]]['disktype']) + ") " + str(utenti_residui(dic,config['user_fisica'],config['user_virtual'])) + " users left before removing server from provisioning"
            tot_user += utenti_residui(dic,config['user_fisica'],config['user_virtual'])
        else:
            ## altrimenti se ci sono macchine da attivare nel provisioning la attiva e, se e solo se ci e' riuscito, toglie la macchina piena dal provisioning
            if len(available_server) > 0:
                if manage_server(list(available_server.keys())[0],"true"):
                    print "insert " + list(available_server.keys())[0] + " into provisioning"
                    new_server = {}
                    server = available_server.keys()[0]
                    new_server[server] = available_server.pop(server)
                    tot_user += utenti_residui(new_server,config['user_fisica'],config['user_virtual'])
                    if manage_server(active_server[i],"false"):
                        print "remove " + active_server[i] + " from provisioning"
                    else:
                        print "\033[1;31;40m" + active_server[i] + " to be removed from provisioning\033[1;37;40m"
                else:
                    print "\033[1;31;40mcant insert into provisioning server " + list(available_server())[0] + ", dont remove server " + active_server[i] + ": disk free " + str(dic[active_server[i]]['df']) + "%, users: " + str(dic[active_server[i]]['users']) + " (disk type " + str(dic[active_server[i]]['disktype']) + ")\033[1;37;40m"
            else:
                print "\033[1;31;40m" + active_server[i] + " to be removed from provisioning but i dont have any spare servers to insert\033[1;37;40m"

    ## stampa a video le macchine inseribili nel provisioning con la somma degli utenti
    lista_macchine = ""
    if len(available_server) > 0:
        for k in available_server:
            lista_macchine = lista_macchine + "," + k
    if general_config['verbose']:
        print "servers already installed: " + str(len(available_server)) + " (" + lista_macchine[1:] + ") for a total of " + str(utenti_residui(available_server,config['user_fisica'],config['user_virtual'])) + " users"

    ## calcola i giorni residui in base alle previsioni presenti nel file di configurazione
    tot_user += utenti_residui(available_server,config['user_fisica'],config['user_virtual'])
    day_left = tot_user/int(config['user_per_day'])
    if day_left > int(general_config['day_warning']):
        if general_config['verbose']:
            print "total users to be activated: " + str(tot_user) + " ended in " + str(day_left) + " days"
    elif day_left > int(general_config['day_critical']):
        if general_config['verbose']:
            print "\033[33mtotal users to be activated: " + str(tot_user) + " ended in " + str(day_left) + " days\033[1;37;40m"
    else:
        ## se abbiamo meno di 7 giorni di autonomia prepariamo una nuova macchina
        print str("\033[1;31;40m" + config['brand'] +": total users to be activated: " + str(tot_user) + " ended in " + str(day_left) + " days\033[1;37;40m")
        if not general_config['dontinstall']:
            ## se ci sono piu' server_farm cicla e usa la prima disponibile
            for server_farm in config['preferred_serverfarm']:
                if macchine_da_inserire[server_farm]:
                    macchina_da_inserire= macchine_da_inserire[server_farm].pop(0)
                    install_new_server(macchina_da_inserire=macchina_da_inserire,general_config=general_config,config=config)
                    break
                else:
                    print "\033[1;31;40mCRITICAL i dont have server to power on on server farm " + server_farm + "\033[1;37;40m"
        else:
            print "dontinstall True dont install new servers"

    return macchine_da_inserire
