#!/usr/bin/python

import suds.client
import ConfigParser
import socket
import subprocess

username = 'admin'
password = "funzionicchiaTutto!1518<"
hostname = socket.gethostname()

configfile = '/etc/r1soft.ini'
file_path = '/root/r1soft-cpanel-plugin-2.0/r1redirect.php'
#dst_path  = '/usr/local/cpanel/base/frontend/paper_lantern/'
dst_path  = '/tmp'
config = ConfigParser.ConfigParser()
config.read(configfile)

cdp_host = config.get('r1soft','url')


class MetaClient(object):
    def __init__(self, url_base, **kwargs):
        self.__url_base = url_base
        self.__init_args = kwargs
        self.__clients = dict()

    def __getattr__(self, name):
        c = self.__clients.get(name, None)
        if c is None:
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
    return url

if __name__ == '__main__':

    client = MetaClient(get_wsdl_url(cdp_host, '%s'), username=username, password=password, faults=True)
    print("Connessione server backup:" + cdp_host )
    servers=client.Policy2.service.getPolicies()

    for server in servers:
        if server.name == hostname:
            CP=server.controlPanelInstanceList[0].id

    print("Modifico file r1redirect.php....")
    subprocess.call(['sed','-i','s/<ID>/%s/' % CP,file_path])
    subprocess.call(['sed','-i','s/<URL>/https:\/\/%s/' % cdp_host,file_path])
    print("Copio file")
    subprocess.call(['cp','%s' % file_path, '%s' % dst_path])
