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

def check_macchina(host='', max_user_virtual=300,max_user_fisica=800,perc_free=30):
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

    max_user = {}
    max_user['virtual'] = max_user_virtual
    max_user['default'] = max_user_fisica

    es = Elasticsearch([{'host': '172.22.131.66', 'port': 9200}])

    request = '{"aggs": {"hostname": {"terms": {"field": "host.name","size": 1000,"order": {"_count": "desc"}},"aggs": {"df": {"terms": {"field": "perc_disk_free","size": 1000,"order": {"_count": "desc"}},"aggs": {"users": {"terms": {"field": "tot_users_real","size": 1000,"order": {"_count": "desc"}},"aggs": {"disktype": {"terms": {"field": "disk_type","size": 5,"order": {"_count": "desc"}},"aggs": {"crtl": {"terms": {"field": "ctrl_type","size": 1000,"order": {"_count": "desc"}}}}}}}}}}}},"size": 0,"version": true,"_source": {"excludes": []},"query": {"bool": {"must": [{"range": {"@timestamp": {"gte": "now-80m","lte": "now"}}},{"match_phrase": {"host.name": {"query": "' + host + '"}}}]}}}'

    #print request
    res = es.search(index="systems-*", body=request )

    ##print res ## debug only

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

## TODO: gestire l'errore
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

def get_ipaddr(vm):
    """ data una macchina ritorna l'indirizzo ip"""
    hnum = re.findall("\d+$",vm)
    ip4 = str(int(hnum[0][1:4]))
    if int(hnum[0][0]) == 0:
        ## macchina lhcp0xxx
        ip1 = "81.88."
        ip3 = str(62 + int(hnum[0][0]))
    else:
        ## macchina lhcp[12]xxx
        ip1 = "185.2."
        ip3 = str(3 + int(hnum[0][0]))
    ipaddr = ip1 + ip3 + "." + ip4
    return ipaddr

def get_ipaddr_eth1(vm):
    """ data una macchina ritorna l'indirizzo ip della eth1"""
    hnum = re.findall("\d+$",vm)
    ip4 = str(int(hnum[0][1:4]))
    ip1 = "172.22."
    ip3 = str(15 + int(hnum[0][0]))
    ipaddr = ip1 + ip3 + "." + ip4
    return ipaddr

def cerca_backup():
    """ cerca la macchina lhbk e il device con meno risorse in termine di: """
    """ - numero lhcp che fanno backup sul device; - spazio libero sul device. """
    """ restituisce un dizionario contenente device, host, perc_used_disk, num_lhcp: """
    """ {'device': u'sdb', 'host': u'lhbk2002.webapps.net', 'perc_used_disk': 1, 'num_lhcp': 0} """

    es = Elasticsearch([{'host': '172.22.131.66', 'port': 9200}])
    request = '{"aggs": { "hostname": { "terms": { "field": "beat.hostname", "size": 5, "order": { "_count": "desc" } }, "aggs": { "device": { "terms": { "field": "device", "size": 5, "order": { "_count": "desc" } }, "aggs": { "num_lhcp": { "terms": {"field": "num_lhcp", "size": 5, "order": { "_count": "desc" } }, "aggs": { "perc_used_disk": { "terms": { "field": "perc_used_disk", "size": 5, "order": { "_count": "desc" } } } } } } } } } }, "size": 0, "version": true, "_source": { "excludes": [] }, "stored_fields": [ "*" ], "script_fields": {}, "docvalue_fields": [ { "field": "@timestamp", "format": "date_time"}],"query": {"bool": {"must": [{"query_string": {"query": "perc_used_disk: [ 0 TO 75 ] AND num_lhcp: [ 0 TO 10]"}},{"match_all": {}},{"range": {"@timestamp": {"gte": "now-140m","lte": "now"}}}],"filter": [],"should": [],"must_not": []}},"highlight": {"pre_tags": ["@kibana-highlighted-field@"],"post_tags": ["@/kibana-highlighted-field@"],"fields": {"*": {}} }}'
    #print request
    res = es.search(index="lhbk-*", body=request )

    #print res ## debug only
    arr=[]
    for hit in res['aggregations']['hostname']['buckets']:
#        print hit
        host = hit['key']
        for hit2 in hit['device']['buckets']:
            device = hit2['key'][5:8]   ## /dev/sdb1 -> sdb
            num_lhcp = hit2['num_lhcp']['buckets'][0]['key']
            perc_used_disk = hit2['num_lhcp']['buckets'][0]['perc_used_disk']['buckets'][0]['key']
            arr.append ({ 'host': host, 'device': device, 'num_lhcp': num_lhcp, 'perc_used_disk': perc_used_disk })

    #print arr
    newlist = sorted(arr, key=lambda k: (k['num_lhcp'], k['perc_used_disk']))
    if len(newlist) > 0:
        return newlist.pop(0)
    return []

def valida_macchine(server=[],max_user_virtual=300,max_user_fisica=800,perc_free=30):
    """ data una lista di macchine con i relativi parametri (max_user,perc_free) """
    """ ritorna un dizionario con le sole macchine papabili per il provisioning come chiave """
    """ e i seguenti valori {'df': 25, 'users': 637, 'virtual': False, 'disktype': u'SSD'} """

    prov_ssd = {}
    for macchina in server:
        tmp_ssd = {}
        tmp_ssd,res = check_macchina(macchina,max_user_virtual,max_user_fisica,perc_free)
        if res:
            prov_ssd.update(tmp_ssd)

    return prov_ssd

## Da cancellare
def cerca_macchine(brand='',max_user_virtual=300,max_user_default=800,perc_free=30,active="false"):
    """ dato un brand cerca le macchine disponibili con i criteri specificati nel file di configurazione """
    """ in termini di massimo numero di utenti per macchine e percentuale di spazio disco libero """
    """ questi valori nel file di configurazione sono personalizzabili per brand e differenziabili """
    """ fra tipologia di macchina (fisica o virtuale) """
    max_user = {}
    max_user['virtual'] = max_user_virtual
    max_user['default'] = max_user_default

    es = Elasticsearch([{'host': '172.22.131.66', 'port': 9200}])

    request = '{"aggs": {"hostname": { "terms": { "field": "host.name", "size": 1000, "order": { "_count": "desc" } }, "aggs": { "df": { "terms": { "field": "perc_disk_free", "size": 1000, "order": {"_count": "desc" } }, "aggs": { "users": {"terms": {"field": "tot_users_real","size": 1000,"order": {"_count": "desc"}},"aggs": {"disktype": {"terms": {"field": "disk_type","size": 5,"order": {"_count": "desc"}},"aggs": {"controller": {"terms": { "field": "ctrl_type", "size": 1000, "order": { "_count": "desc" }}}}}} } } } }}},"size": 0,"version": true,"_source": {"excludes": []},"query": {"bool": { "must": [ { "query_string": { "query": "perc_disk_free: ['  + str(perc_free) + ' TO 100] AND isActive: ' + active + '", "analyze_wildcard": true, "default_field": "*" } }, { "range": { "@timestamp": {"gte": "now-80m","lte": "now" } } }, { "match_phrase": { "wholesaler": {"query": "' + brand + '" } } } ]}}}'
    #print request
    res = es.search(index="systems-*", body=request )

    #print res ## debug only
    dic = {}
    dic_sas = {}

    for hit in res['aggregations']['hostname']['buckets']:
        hostname = hit['key']
        df = hit['df']['buckets'][0]['key']
        users = hit['df']['buckets'][0]['users']['buckets'][0]['key']
        disktype =  hit['df']['buckets'][0]['users']['buckets'][0]['disktype']['buckets'][0]['key']
        controller = hit['df']['buckets'][0]['users']['buckets'][0]['disktype']['buckets'][0]['controller']['buckets'][0]['key']
        if controller == 'VMWare':
            virtual = True
            maxu = max_user['virtual']
            ## le virtuali hanno tutte dischi SSD
            disktype = "SSD"
        else:
            virtual = False
            maxu = max_user['default']
        #if df >= perc_free and max > users:
        if int(maxu) > int(users):
            if disktype == "SSD":
                if not hostname in dic.keys():
                    if not check_server(hostname):
                        dic[hostname] = { 'df': df, 'users': users, 'disktype': disktype, 'virtual': virtual }
            else:
                if not hostname in dic_sas.keys():
                    if not check_server(hostname):
                        dic_sas[hostname] = { 'df': df, 'users': users, 'disktype': disktype, 'virtual': virtual }
        else:
            if active == "true":
                print "togli dal provisioning la macchina " + hostname + " perche' ha " + str(users) + " utenti (virtual= " + str(virtual) + ")"
            #else:
            #    print "scarto "+ hostname + " perche' ha " + str(users) + " utenti (virtual= " + str(virtual) + ")"

    return dic,dic_sas

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
    """given a server activate/disactivate the instance"""
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

        bashCommand = "cd " + puppet_path + " && svn up"
        os.system(bashCommand)

        f = open(puppet_path + "/" + f,"a")
        f.write("\n" + vm + ".webapps.net\n")
        f.close()

        bashCommand = "cd " + puppet_path + " && svn ci -m 'autoadd " + vm + " to autosign'"
        os.system(bashCommand)

        print "puppet run"
        ipaddr = get_ipaddr(vm)
        bashCommand = "ssh -oStrictHostKeyChecking=no -p 25088 root@" + ipaddr + " 'puppet agent -t'"
        os.system(bashCommand)
        return True
    return False

def configure_naemon(vm,puppet_template,puppet_path):
    """ data una macchina e il relativo template da utilizzare configura puppet """
    """ prende come variabile di input anche il path dove sta la configurazione di puppet """
    """ controlla che il path dove sta la configurazione sia corretto e che la macchina """
    """ non sia gia' sotto puppet """
    if os.path.isdir(puppet_path):
        p = puppet_path + "/modules/naemon/files/naemon/conf.d_register/puwebhosting/"
        conffile = p + "uk_cpanel_hosts.cfg"
        bashCommand = "cd " + p + " && svn up"
        os.system(bashCommand)

        ## controllo che la macchina non sia gia' sotto puppet
        if vm in open(conffile).read():
            print "macchina " + vm + " gia' presente su puppet"
        else:
            f = open(conffile,"a")

            f.write("define host {\n")
            f.write("    host_name       " + vm + ".webapps.net\n")
            f.write("    _SHORTNAME      " + vm + "\n")
            f.write("     address        " + vm + ".webapps.net\n")
            f.write("     use            lhcp-virtual," + puppet_template + "\n")
            f.write("}\n")
            f.close()

            bashCommand = "cd " + p + " && svn ci -m 'autoadd " + vm + " to puppet'"
            os.system(bashCommand)
            time.sleep(5)

        bashCommand = "ssh root@anael01.it.dadainternal 'puppet agent -t'"
        os.system(bashCommand)
        return True
    return False

def vmware_configure_server(vm):
    """ data una macchina la configura """
    ipaddr1 = get_ipaddr(vm)
    ipaddr2 = get_ipaddr_eth1(vm)
    with open('auto_install.sh', 'r') as file:
        filedata = file.read()

    dic = cerca_backup()
    # Replace the target string
    filedata = filedata.replace('FAKEHOSTNAME', vm + '.webapps.net')
    filedata = filedata.replace('FAKEIPADDR1', ipaddr1)
    filedata = filedata.replace('FAKEIPADDR2', ipaddr2)
    filedata = filedata.replace('FAKEBACKUPSERVER', dic['host'])
    filedata = filedata.replace('FAKEHOUR', str(dic['num_lhcp']).zfill(2))  ## TODO: vedere se e' il caso di usare il metodo muzz e verificare script niccoli
    filedata = filedata.replace('FAKEVOLUME', dic['device'])

    # Write the file out again
    with open('auto_install2.sh', 'w') as file:
        file.write(filedata)

    temporary_ipaddr = "185.2.6.241"
    ## copia i files sulla macchina (dovrebbero essere sul template)
    bashCommand = "scp -P 25088 auto_install2.sh root@" + temporary_ipaddr + ":/root/auto_install.sh"
    os.system(bashCommand)
    bashCommand = "ssh -oStrictHostKeyChecking=no -p 25088 root@" + temporary_ipaddr + " 'chmod +x /root/auto_install.sh'"
    os.system(bashCommand)

    bashCommand = "scp -P 25088 estrai_cPanel_id.py root@" + temporary_ipaddr + ":/usr/local/scripts/"
    os.system(bashCommand)

    bashCommand = "ssh -oStrictHostKeyChecking=no -p 25088 root@" + temporary_ipaddr + " '/root/auto_install.sh'"
    os.system(bashCommand)

    bashCommand = "ssh -oStrictHostKeyChecking=no -p 25088 root@" + temporary_ipaddr + " 'reboot'"
    os.system(bashCommand)

def softaculous_licence(vm):
    """ data una macchina attiva la licenza softaculous """
    ipaddr = get_ipaddr(vm)

    with open('soft.php', 'r') as file:
        filedata = file.read()

    # Replace the target string
    filedata = filedata.replace('FAKEIPADDR', ipaddr)

    # Write the file out again
    with open('soft2.php', 'w') as file:
        file.write(filedata)

    bashCommand = "php ./soft2.php"
    os.system(bashCommand)

    bashCommand = "ssh -oStrictHostKeyChecking=no -p 25088 root@" + ipaddr + " '/usr/local/cpanel/3rdparty/bin/php /usr/local/cpanel/whostmgr/docroot/cgi/softaculous/cron.php && /usr/local/cpanel/3rdparty/bin/php /usr/local/cpanel/whostmgr/docroot/cgi/softaculous/cli.php -l'"
    os.system(bashCommand)

def activate_cloudlinux_license(vm):
    """ dato un indirizzo ip attiva le licenze di cloudlinux """
    ipaddr = get_ipaddr(vm)
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

def create_dns_record(vm):
    """ data una macchina crea i record dns necessari"""
    ipaddr = get_ipaddr(vm)
    bashCommand = "ssh root@git01.it.dadainternal /root/daniele/add_lhcp.pl " + vm + ".webapps.net " + ipaddr
    os.system(bashCommand)

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


def vmware_getavailableserver(host,user,pwd,port=443):
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
                    macchine_da_inserire = macchine_da_inserire + name
    print "ci sono " + str(len(macchine_da_inserire)) + " macchine da inserire nel provisioning:"
    macchine_da_inserire.sort()
    for n in macchine_da_inserire:
        print n,
    print
    return macchine_da_inserire

def read_config(file):
    """ legge da un file di configurazione e ritorna un dizionario con le configurazioni """

    # Lettura del file di configurazione
    config = ConfigParser.ConfigParser()
    config.read(file)

    conf = {}
    ## TODO: gestire l'errore nel caso in cui manchi un parametro (prevedere un default)
    conf['general'] = { 'host': config.get('general','host'), 'user': config.get('general','user'), 'pass': config.get('general','pass'), 'brand': config.get('general','brand'), 'puppet_path': config.get('general','puppet_path') }
    for brand in conf['general']['brand'].split(','):
        conf[brand]= { 'brand': config.get(brand,'brand'), 'user_fisica': config.get(brand,'user_fisica'), 'user_virtual': config.get(brand,'user_virtual'), 'disk': config.get(brand,'disk'), 'user_per_day': config.get(brand,'user_per_day'), 'wh': config.get(brand,'wh'), 'puppet_template': config.get(brand,'puppet_template'), 'tags': config.get(brand,'tags').split(",") }
    return conf

def controlla_macchine(active_server=[],available_server=[],config=[],macchine_da_inserire=[],general_config=[]):
    """ date 2 liste: """
    """ - active_server: le macchine attive sul provisioning """
    """ - available_server: le macchine disponibili """
    """ controlla se fra gli active_server qualcuno ha raggiunto i limiti """
    """ in caso affermativo prima inserisce una nuova macchina nel provisioning """
    """ e, se e solo se la nuova macchina e' stata aggiunta nel provisioning """
    """ provvede a rimuovere la vecchia macchina nel provisioning """

    tot_user = 0

    ## per ogni macchina attiva nel provisioning
    for i in range(len(active_server)):
        ## controlla che possa rimanere ancora nel provisioning
        dic,res=check_macchina(host=active_server[i],max_user_virtual=config['user_virtual'],max_user_fisica=config['user_fisica'],perc_free=config['disk'])

        #print available_server
        #print dic
        #print res
        if res:
            print active_server[i] + " ok, disco libero " + str(dic[active_server[i]]['df']) + "% e " + str(dic[active_server[i]]['users']) + " utenti (disco " + str(dic[active_server[i]]['disktype']) + ") mancano " + str(utenti_residui(dic,config['user_fisica'],config['user_virtual'])) + " utenti prima di togliere la macchina dal provisioning"
            tot_user += utenti_residui(dic,config['user_fisica'],config['user_virtual'])
        else:
            ## altrimenti se ci sono macchine da attivare nel provisioning la attiva e, se e solo se ci e' riuscito, toglie la macchina piena dal provisioning
            if len(available_server) > 0:
                if manage_server(list(available_server.keys())[0],"true"):
                    print "inserita nel provisioning la macchina " + list(available_server.keys())[0]
                    new_server = {}
                    server = available_server.keys()[0]
                    new_server[server] = available_server.pop(server)
                    tot_user += utenti_residui(new_server,config['user_fisica'],config['user_virtual'])
                    if manage_server(active_server[i],"false"):
                        print "tolta " + active_server[i] + " dal provisioning"
                    else:
                        print "\033[1;31;40m" + active_server[i] + " da togliere dal provisioning\033[1;37;40m"
                else:
                    print "\033[1;31;40mnon riesco ad inserire nel provisioning la macchina " + list(available_server())[0] + ", di conseguenza non tolgo la macchina " + active_server[i] + " da togliere dal provisioning: disco libero " + str(dic[active_server[i]]['df']) + "% e " + str(dic[active_server[i]]['users']) + " utenti (disco " + str(dic[active_server[i]]['disktype']) + ")\033[1;37;40m"
            else:
                print "\033[1;31;40m" + active_server[i] + " da togliere dal provisioning ma purtroppo non ho macchine di spare da inserire\033[1;37;40m"

    ## stampa a video le macchine inseribili nel provisioning con la somma degli utenti
    lista_macchine = ""
    if len(available_server) > 0:
        for k in available_server:
            lista_macchine = lista_macchine + "," + k
    print "macchine con dischi SSD inseribili nel provisioning: " + str(len(available_server)) + " (" + lista_macchine[1:] + ") per un totale di " + str(utenti_residui(available_server,config['user_fisica'],config['user_virtual'])) + " utenti"

    ## calcola i giorni residui in base alle previsioni presenti nel file di configurazione
    tot_user += utenti_residui(available_server,config['user_fisica'],config['user_virtual'])
    day_left = tot_user/int(config['user_per_day'])
    if day_left > 14:
        print "utenti totali da attivare: " + str(tot_user) + " sufficienti per " + str(day_left) + " giorni"
    elif day_left > 7:
        print "\033[33mutenti totali da attivare: " + str(tot_user) + " sufficienti per " + str(day_left) + " giorni\033[1;37;40m"
    else:
        ## se abbiamo meno di 7 giorni di autonomia prepariamo una nuova macchina
        print "\033[1;31;40mutenti totali da attivare: " + str(tot_user) + " sufficienti per " + str(day_left) + " giorni\033[1;37;40m"
        if macchine_da_inserire:
            macchina_da_inserire = macchine_da_inserire.pop(0)
            print "metto una macchina nuova nel provisioning (" + macchina_da_inserire + ")"
            content=vmware_connect(general_config['host'],general_config['user'],general_config['pass'])
            vmware_poweron(macchina_da_inserire,content)
            insertServerInProvisioning(macchina_da_inserire,config['wh'],config['tags'])
            activate_cloudlinux_license(macchina_da_inserire)
            create_dns_record(macchina_da_inserire)
            time.sleep(60)
            vmware_configure_server(macchina_da_inserire)
            time.sleep(60)
            softaculous_licence(macchina_da_inserire)
            configure_puppet(macchina_da_inserire,general_config['puppet_path'])
            configure_naemon(macchina_da_inserire,config['puppet_template'],general_config['puppet_path'])
        else:
            print "\033[1;31;40mATTENZIONE non ho macchine da inserire\033[1;37;40m"

    ## TODO: controllo per aprire il task a infra per la creazione di nuove macchine
    if len(macchine_da_inserire) < 5:
        print "\033[1;31;40mATTENZIONE ci sono solo " + str(len(macchine_da_inserire)) + " macchine da inserire, aprire un task a ct-infra per farsi creare nuove macchine\033[1;37;40m"
    else:
        print "tranquillo ci sono " + str(len(macchine_da_inserire)) + " macchine da inserire"
    ## TODO: licenze cpanel (mail a chirag)
