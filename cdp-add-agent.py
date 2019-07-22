#!/usr/bin/python
#
# Modifica effettuata da Emiliano Muzzurru Renzi per CDPSERVER v.6.8
#
# CHANGELOG
#  - Aggiunte exception con procedura di rollback in caso di fault creazione policy

import suds.client
import logging
import ConfigParser
import os
import sys
import socket

configfile = '/etc/r1soft.ini'
mysqlconfigfile = '/root/.my.cnf'

if not os.path.exists(configfile):
        print "Il file di configurazione di r1soft non esiste, crealo please..."
        sys.exit()

# Prendo i dati dal file di configurazione:
config = ConfigParser.ConfigParser()
config.read(configfile)

#Popolo le variabili

cdp_host = config.get('r1soft','url')
recovery_point_limit = config.get('r1soft','recovery_point_limit')
volume = config.get('r1soft','volume')
cp_name = config.get('r1soft','cp_name')
tmphours=config.get('r1soft','hours')
#Converto la stringa tmphours in un array numerico da passare alla policy
hours=map(int, tmphours.split(','))

minutes=config.get('r1soft','minutes')

# Eseguo r1soft-setup --get-key con il parametro il nome dell'host specificato nel file /etc/r1soft.ini
comando_r1soft="r1soft-setup --get-key https://"+cdp_host
os.system(comando_r1soft)

username = 'admin'
password = "funzionicchiaTutto!1518<"

use_db_addon = True
sqluser = 'root'

hostname = socket.gethostname()
description = hostname


# Prendo i dati dal file di configurazione:
config = ConfigParser.ConfigParser()
config.read(mysqlconfigfile)
tempsqlpass = config.get('client','password')
sqlpass = tempsqlpass.replace('"', "")

logger = logging.getLogger('cdp-add-agent')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
logger.propagate = False

class MetaClient(object):
    def __init__(self, url_base, **kwargs):
        self.__url_base = url_base
        self.__init_args = kwargs
        self.__clients = dict()

    def __getattr__(self, name):
        c = self.__clients.get(name, None)
        logger.debug('Accessing SOAP client: %s' % name)
        if c is None:
            logger.debug('Client doesn\'t exist, creating: %s' % name)
            c = suds.client.Client(self.__url_base % name, **self.__init_args)
            self.__clients[name] = c
        return c

def get_wsdl_url(hostname, namespace, use_ssl=True, port_override=None):
    if use_ssl:
        proto = 'https'
    else:
        proto = 'http'
    if port_override is None:
        if use_ssl:
            port = 9443
        else:
            port = 9080
    else:
        port = port_override
    url = '%s://%s:%d/%s?wsdl' % (proto, hostname, port, namespace)
    logging.debug('Creating WSDL URL: %s' % url)
    return url

def rollback_exception(hostname):

    for i in client.Policy2.service.getPolicies():
        if i.description == hostname:
            client.Policy2.service.deletePolicyById(i.id)
            print("Remove policy " + hostname)

    for i in client.DiskSafe.service.getDiskSafes():
        if i.description == hostname:
            client.DiskSafe.service.deleteDiskSafeById(i.id)
            print("Remove Disksafe " + hostname)

    for i in client.Agent.service.getAgents():
        if i.description == hostname:
            client.Agent.service.deleteAgentById(i.id)
            print("Remove Agent " + hostname)

if __name__ == '__main__':
    import sys
    import os

    logger.info('Setting up backups for host (%s) on CDP server (%s) with description: %s', hostname, cdp_host, description)
    client = MetaClient(get_wsdl_url(cdp_host, '%s'), username=username, password=password,faults=True)
    logger.debug('Creating special types...')
    DiskSafeObject = client.DiskSafe.factory.create('diskSafe.disksafe')
    CompressionType = client.DiskSafe.factory.create('diskSafe.compressionType')
    CompressionLevel = client.DiskSafe.factory.create('diskSafe.compressionLevel')
    DeviceBackupType = client.DiskSafe.factory.create('diskSafe.deviceBackupType')
    FrequencyType = client.Policy2.factory.create('frequencyType')
    FrequencyValues = client.Policy2.factory.create('frequencyValues')
    ControlPanelList = client.Policy2.factory.create('policy.controlPanelInstanceList')
    ExcludeList = client.Policy2.factory.create('policy.excludeList')
    ExcludeList2 = client.Policy2.factory.create('policy.excludeList')
    ExcludeList3 = client.Policy2.factory.create('policy.excludeList')
    ExcludeList4 = client.Policy2.factory.create('policy.excludeList')
    ExcludeList5 = client.Policy2.factory.create('policy.excludeList')
    ExcludeList6 = client.Policy2.factory.create('policy.excludeList')
    ExcludeList7 = client.Policy2.factory.create('policy.excludeList')
    ExcludeList8 = client.Policy2.factory.create('policy.excludeList')
    ExcludeList9 = client.Policy2.factory.create('policy.excludeList')

    ### Remove code
    logger.debug('Created special types')
    logger.debug('Getting volumes...')
    volumes = client.Volume.service.getVolumes()
    # Scelgo il volume su cui backuppare. Controllo solo se e' sda perche' tanto r1soft ha solo sda o sdb

    trovato=False;
    for volumi in volumes:
        if volumi.name == volume:
            ID_Volume=volumi.id
            print(ID_Volume)
            trovato=True

    if trovato == False:
       print "Errore device nella configurazione"
       sys.exit(1)

    logger.info('Using volume %s', volume)
    logger.debug('Creating agent for host: %s', hostname)
    try:
        agent = client.Agent.service.createAgent(
            hostname=hostname,
            portNumber=1167,
            description=description,
            databaseAddOnEnabled=use_db_addon
        )
    except suds.WebFault as detail:
        print(detail)
    else:
        logger.info('Created agent for host (%s) with ID: %s', hostname, agent.id)
        logger.debug('Creating disksafe for agent (%s) on volume (%s)', agent.id, volume)
        DiskSafeObject.description = hostname
        DiskSafeObject.agentID = agent.id
        DiskSafeObject.volumeID = ID_Volume
        DiskSafeObject.compressionType = CompressionType.QUICKLZ
        DiskSafeObject.compressionLevel = CompressionLevel.HIGH
        DiskSafeObject.deviceBackupType = DeviceBackupType.AUTO_ADD_DEVICES
        DiskSafeObject.backupPartitionTable = False
        DiskSafeObject.backupUnmountedDevices = False
        disksafe = client.DiskSafe.service.createDiskSafeWithObject(DiskSafeObject)
        logger.info('Created disksafe with ID: %s', disksafe.id)
        FrequencyValues.hoursOfDay = hours
        FrequencyValues.daysOfWeek = ['SUNDAY','MONDAY','TUESDAY','WEDNESDAY','THURSDAY','FRIDAY','SATURDAY']
        FrequencyValues.startingHour = hours
        FrequencyValues.startingMinute = minutes
        logger.debug('Creating policy for agent (%s) on disksafe (%s)',
            hostname, disksafe.id)
        policy = client.Policy2.factory.create('policy')
        policy.enabled = True
        policy.name = hostname
        policy.description = description
        policy.diskSafeID = disksafe.id
        policy.mergeScheduleFrequencyType = FrequencyType.ON_DEMAND
        policy.replicationScheduleFrequencyType = FrequencyType.DAILY
        policy.replicationScheduleFrequencyValues = FrequencyValues
        policy.recoveryPointLimit = recovery_point_limit
        policy.forceFullBlockScan = False
        policy.localArchivingEnabled = True
        policy.localRetentionSettings.dailyLimit=7
        policy.localRetentionSettings.weeklyLimit=2
        ExcludeList.exclusionPattern="/home/*/.trash/"
        ExcludeList.isRecursive=False
        ExcludeList2.exclusionPattern="/home/*/public_html/error_log"
        ExcludeList2.isRecursive=False
        ExcludeList3.exclusionPattern="/backup"
        ExcludeList3.isRecursive=False
        ExcludeList4.exclusionPattern="/var/tmp"
        ExcludeList4.isRecursive=False
        ExcludeList5.exclusionPattern="/var/log"
        ExcludeList5.isRecursive=False
        ExcludeList6.exclusionPattern="/usr/local/apache/domlogs"
        ExcludeList6.isRecursive=False
        ExcludeList7.exclusionPattern="/usr/local/apache/logs"
        ExcludeList7.isRecursive=False
        ExcludeList8.exclusionPattern="/usr/tmp"
        ExcludeList8.isRecursive=False
        ExcludeList9.exclusionPattern="/usr/tmpDISK"
        ExcludeList9.isRecursive=False
        policy.excludeList=[ExcludeList,ExcludeList2,ExcludeList3,ExcludeList4,ExcludeList5,ExcludeList6,ExcludeList7,ExcludeList8,ExcludeList9]
    
        ControlPanelList.controlPanelType="CPANEL"
        ControlPanelList.enabled="true"
        ControlPanelList.name=cp_name
        policy.controlPanelInstanceList=[ControlPanelList]
 
        if use_db_addon:
            dbi = client.Policy2.factory.create('databaseInstance')
            dbi.dataBaseType = client.Policy2.factory.create('dataBaseType').MYSQL
            dbi.enabled = True
            dbi.hostName = 'localhost'
            dbi.name = 'default'
            dbi.username = sqluser
            dbi.password = sqlpass
            dbi.portNumber = 3306
            dbi.useAlternateDataDirectory = False
            dbi.useAlternateHostname = True
            dbi.useAlternateInstallDirectory = False
            policy.databaseInstanceList = [dbi]

        try:
            policy = client.Policy2.service.createPolicy(policy=policy)
        except suds.WebFault as detail:
            print("Problem with generation Policy. Rollback...")
            rollback_exception(hostname)
            sys.exit(1)

        logger.info('Created policy with ID: %s', policy.id)
        logger.info('Finished setting up backups for host: %s', hostname)

