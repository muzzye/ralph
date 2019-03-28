#!/bin/bash

## --- inizio parametri ---
HOSTNAME="FAKEHOSTNAME"
IPADDR="FAKEIPADDR1"
IPADDR2="FAKEIPADDR2"
R1SOFT_BACKUP_SERVER="FAKEBACKUPSERVER"
BACKUP_HOUR="FAKEHOUR"
BACKUP_MINUTE="40"
BACKUP_VOLUME="FAKEVOLUME"
## --- fine parametri ---

## hostname
/usr/local/cpanel/bin/set_hostname ${HOSTNAME}

## ip addr
sed -i "s/^IPADDR=\(.*\)/IPADDR=${IPADDR}/g" /etc/sysconfig/network-scripts/ifcfg-eth0
sed -i "s/^IPADDR=\(.*\)/IPADDR=${IPADDR2}/g" /etc/sysconfig/network-scripts/ifcfg-eth1
echo "${IPADDR}" > /etc/ips
echo "${IPADDR}" > /var/cpanel/mainip
echo -e "${IPADDR}\t\t${HOSTNAME} ${HOSTNAME%%.*}" >> /etc/hosts

## rimozione file inutili
#rm -rf /root/.ssh/authorized_keys
rm -rf /etc/udev/rules.d/70-persistent-net.rules

#configurazione r1soft
sed -i "s/^url\(.*\)/url = ${R1SOFT_BACKUP_SERVER}/g" /etc/r1soft.ini
sed -i "s/^hours\(.*\)/hours = ${BACKUP_HOUR}/g" /etc/r1soft.ini
sed -i "s/^minutes\(.*\)/minutes = ${BACKUP_MINUTE}/g" /etc/r1soft.ini
sed -i "s/^volume\(.*\)/volume = ${BACKUP_VOLUME}/g" /etc/r1soft.ini
sed -i "s/^cp_name\(.*\)/cp_name = cp_${HOSTNAME%%.*}/g" /etc/r1soft.ini

cdp-add-agent.py

chmod +x /usr/local/scripts/estrai_cPanel_id.py
/usr/local/scripts/estrai_cPanel_id.py ${HOSTNAME}
/usr/local/cpanel/scripts/install_plugin r1soft-cpanel-plugin-2.0 --theme paper_lantern

## registrazione cloudlinux
/usr/sbin/clnreg_ks --force

## deploy cic
puppi deploy cpanel-instance-client
