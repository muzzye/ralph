# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ralph.networks.fields
import ralph.lib.mixins.fields
import ralph.lib.mixins.models
import mptt.fields
import django.db.models.deletion
import ralph.networks.models.networks


class Migration(migrations.Migration):

    dependencies = [
        ('data_center', '0001_initial'),
        ('assets', '0001_initial'),
        ('dhcp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiscoveryQueue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=255, unique=True)),
            ],
            options={
                'verbose_name': 'discovery queue',
                'verbose_name_plural': 'discovery queues',
                'ordering': ('name',),
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='IPAddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
                ('last_seen', models.DateTimeField(verbose_name='last seen', auto_now_add=True)),
                ('address', models.GenericIPAddressField(verbose_name='IP address', unique=True, help_text='Presented as string.')),
                ('hostname', ralph.lib.mixins.fields.NullableCharField(verbose_name='hostname', max_length=255, blank=True, null=True, default=None)),
                ('number', models.DecimalField(verbose_name='IP address', unique=True, default=None, editable=False, help_text='Presented as int.', max_digits=39, decimal_places=0)),
                ('is_management', models.BooleanField(verbose_name='Is management address', default=False)),
                ('is_public', models.BooleanField(verbose_name='Is public', default=False, editable=False)),
                ('is_gateway', models.BooleanField(verbose_name='Is gateway', default=False)),
                ('status', models.PositiveSmallIntegerField(default=1, choices=[(1, 'used (fixed address in DHCP)'), (2, 'reserved')])),
                ('dhcp_expose', models.BooleanField(verbose_name='Expose in DHCP', default=False)),
                ('ethernet', models.OneToOneField(blank=True, null=True, default=None, to='assets.Ethernet')),
            ],
            options={
                'verbose_name': 'IP address',
                'verbose_name_plural': 'IP addresses',
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, ralph.networks.models.networks.NetworkMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Network',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=255, unique=True)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
                ('address', ralph.networks.fields.IPNetwork(verbose_name='network address', max_length=44, unique=True, help_text='Presented as string (e.g. 192.168.0.0/24)')),
                ('remarks', models.TextField(verbose_name='remarks', blank=True, default='', help_text='Additional information.')),
                ('vlan', models.PositiveIntegerField(verbose_name='VLAN number', blank=True, null=True, default=None)),
                ('min_ip', models.DecimalField(verbose_name='smallest IP number', editable=False, max_digits=39, decimal_places=0)),
                ('max_ip', models.DecimalField(verbose_name='largest IP number', editable=False, max_digits=39, decimal_places=0)),
                ('dhcp_broadcast', models.BooleanField(verbose_name='Broadcast in DHCP configuration', db_index=True, default=True)),
                ('reserved_from_beginning', models.PositiveIntegerField(default=10, help_text='Number of addresses to be omitted in DHCP automatic assignmentcounted from the first IP in range (excluding network address)')),
                ('reserved_from_end', models.PositiveIntegerField(default=0, help_text='Number of addresses to be omitted in DHCP automatic assignmentcounted from the last IP in range (excluding broadcast address)')),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('dns_servers_group', models.ForeignKey(blank=True, null=True, related_name='networks', on_delete=django.db.models.deletion.PROTECT, to='dhcp.DNSServerGroup')),
                ('gateway', models.ForeignKey(verbose_name='Gateway address', blank=True, null=True, related_name='gateway_network', on_delete=django.db.models.deletion.SET_NULL, to='networks.IPAddress')),
            ],
            options={
                'verbose_name': 'network',
                'verbose_name_plural': 'networks',
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, ralph.networks.models.networks.NetworkMixin, models.Model),
        ),
        migrations.CreateModel(
            name='NetworkEnvironment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=255, unique=True)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
                ('hostname_template_counter_length', models.PositiveIntegerField(verbose_name='hostname template counter length', default=4)),
                ('hostname_template_prefix', models.CharField(verbose_name='hostname template prefix', max_length=30)),
                ('hostname_template_postfix', models.CharField(verbose_name='hostname template postfix', max_length=30, help_text='This value will be used as a postfix when generating new hostname in this network environment. For example, when prefix is "s1", postfix is ".mydc.net" and counter length is 4, following  hostnames will be generated: s10000.mydc.net, s10001.mydc.net, .., s19999.mydc.net.')),
                ('domain', ralph.lib.mixins.fields.NullableCharField(verbose_name='domain', max_length=255, blank=True, null=True, help_text='Used in DHCP configuration.')),
                ('remarks', models.TextField(verbose_name='remarks', blank=True, null=True, help_text='Additional information.')),
                ('use_hostname_counter', models.BooleanField(default=True, help_text='If set to false hostname based on already added hostnames.')),
                ('data_center', models.ForeignKey(verbose_name='data center', to='data_center.DataCenter')),
                ('queue', models.ForeignKey(verbose_name='discovery queue', blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='networks.DiscoveryQueue')),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='NetworkKind',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=255, unique=True)),
            ],
            options={
                'verbose_name': 'network kind',
                'verbose_name_plural': 'network kinds',
                'ordering': ('name',),
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Vlan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=255, unique=True)),
                ('vlan', models.PositiveIntegerField(verbose_name='VLAN', unique=True, default=None)),
            ],
            options={
                'verbose_name': 'Vlan address',
                'verbose_name_plural': 'Vlan addresses',
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, ralph.networks.models.networks.NetworkMixin, models.Model),
        ),
        migrations.AddField(
            model_name='network',
            name='kind',
            field=models.ForeignKey(verbose_name='network kind', blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='networks.NetworkKind'),
        ),
        migrations.AddField(
            model_name='network',
            name='network_environment',
            field=models.ForeignKey(verbose_name='environment', blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='networks.NetworkEnvironment'),
        ),
        migrations.AddField(
            model_name='network',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, editable=False, related_name='children', to='networks.Network'),
        ),
        migrations.AddField(
            model_name='network',
            name='racks',
            field=models.ManyToManyField(verbose_name='racks', blank=True, to='data_center.Rack'),
        ),
        migrations.AddField(
            model_name='network',
            name='service_env',
            field=models.ForeignKey(blank=True, null=True, default=None, related_name='networks', to='assets.ServiceEnvironment'),
        ),
        migrations.AddField(
            model_name='network',
            name='terminators',
            field=models.ManyToManyField(verbose_name='network terminators', blank=True, to='assets.BaseObject'),
        ),
        migrations.AddField(
            model_name='ipaddress',
            name='network',
            field=models.ForeignKey(null=True, default=None, editable=False, related_name='ips', on_delete=django.db.models.deletion.SET_NULL, to='networks.Network'),
        ),
        migrations.AddField(
            model_name='ipaddress',
            name='vlan',
            field=models.ForeignKey(verbose_name='vlan', blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='networks.Network'),
        ),
        migrations.AlterUniqueTogether(
            name='network',
            unique_together=set([('min_ip', 'max_ip')]),
        ),
    ]
