# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ralph.lib.mixins.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DHCPServer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('ip', models.GenericIPAddressField(verbose_name='IP address', unique=True)),
                ('last_synchronized', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'DHCP Server',
                'verbose_name_plural': 'DHCP Servers',
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='DNSServer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('ip_address', models.GenericIPAddressField(verbose_name='IP address', unique=True)),
            ],
            options={
                'verbose_name': 'DNS Server',
                'verbose_name_plural': 'DNS Servers',
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='DNSServerGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=255, unique=True)),
            ],
            options={
                'verbose_name': 'DNS Server Group',
                'verbose_name_plural': 'DNS Server Groups',
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='DNSServerGroupOrder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('order', models.PositiveIntegerField(db_index=True)),
            ],
            options={
                'ordering': ('order',),
            },
        ),
    ]
