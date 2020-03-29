# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('networks', '0001_initial'),
        ('dhcp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DHCPEntry',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('networks.ipaddress',),
        ),
        migrations.AddField(
            model_name='dnsservergrouporder',
            name='dns_server',
            field=models.ForeignKey(related_name='server_group_order', to='dhcp.DNSServer'),
        ),
        migrations.AddField(
            model_name='dnsservergrouporder',
            name='dns_server_group',
            field=models.ForeignKey(related_name='server_group_order', to='dhcp.DNSServerGroup'),
        ),
        migrations.AddField(
            model_name='dnsservergroup',
            name='servers',
            field=models.ManyToManyField(to='dhcp.DNSServer', through='dhcp.DNSServerGroupOrder'),
        ),
        migrations.AddField(
            model_name='dhcpserver',
            name='network_environment',
            field=models.ForeignKey(blank=True, null=True, to='networks.NetworkEnvironment'),
        ),
        migrations.AlterUniqueTogether(
            name='dnsservergrouporder',
            unique_together=set([('dns_server_group', 'dns_server')]),
        ),
    ]
