# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_extensions.db.fields.json
import django_cryptography.fields
import ralph.lib.mixins.fields
import django.db.models.deletion
import ralph.lib.mixins.models
import ralph.assets.utils
import ralph.lib.transitions.fields


class Migration(migrations.Migration):

    dependencies = [
        ('data_center', '0001_initial'),
        ('assets', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CloudFlavor',
            fields=[
                ('baseobject_ptr', models.OneToOneField(primary_key=True, serialize=False, auto_created=True, parent_link=True, to='assets.BaseObject')),
                ('name', models.CharField(verbose_name='name', max_length=255)),
                ('flavor_id', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, 'assets.baseobject'),
        ),
        migrations.CreateModel(
            name='CloudHost',
            fields=[
                ('baseobject_ptr', models.OneToOneField(primary_key=True, serialize=False, auto_created=True, parent_link=True, to='assets.BaseObject')),
                ('host_id', models.CharField(verbose_name='host ID', max_length=100, unique=True)),
                ('hostname', models.CharField(verbose_name='hostname', max_length=255)),
                ('image_name', models.CharField(max_length=255, blank=True, null=True)),
                ('cloudflavor', models.ForeignKey(verbose_name='Instance Type', to='virtual.CloudFlavor')),
            ],
            options={
                'verbose_name': 'Cloud host',
                'verbose_name_plural': 'Cloud hosts',
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, 'assets.baseobject', models.Model),
        ),
        migrations.CreateModel(
            name='CloudImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('image_id', models.CharField(verbose_name='image ID', max_length=100, unique=True)),
                ('name', models.CharField(max_length=200)),
            ],
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='CloudProject',
            fields=[
                ('baseobject_ptr', models.OneToOneField(primary_key=True, serialize=False, auto_created=True, parent_link=True, to='assets.BaseObject')),
                ('project_id', models.CharField(verbose_name='project ID', max_length=100, unique=True)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, 'assets.baseobject', models.Model),
        ),
        migrations.CreateModel(
            name='CloudProvider',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=255, unique=True)),
                ('cloud_sync_enabled', models.BooleanField(default=False)),
                ('cloud_sync_driver', models.CharField(max_length=128, blank=True, null=True)),
                ('client_config', django_cryptography.fields.encrypt(django_extensions.db.fields.json.JSONField(verbose_name='client configuration', blank=True, null=True, default=dict))),
            ],
            options={
                'verbose_name': 'Cloud provider',
                'verbose_name_plural': 'Cloud providers',
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='VirtualComponent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
                ('model_name', models.CharField(verbose_name='model name', max_length=255, blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='VirtualServer',
            fields=[
                ('baseobject_ptr', models.OneToOneField(primary_key=True, serialize=False, auto_created=True, parent_link=True, to='assets.BaseObject')),
                ('status', ralph.lib.transitions.fields.TransitionField(default=1, choices=[(1, 'new'), (2, 'in use'), (3, 'to deploy'), (4, 'liquidated')])),
                ('hostname', ralph.lib.mixins.fields.NullableCharField(verbose_name='hostname', max_length=255, unique=True, blank=True, null=True, default=None)),
                ('sn', ralph.lib.mixins.fields.NullableCharField(verbose_name='SN', max_length=200, unique=True, blank=True, null=True, default=None)),
                ('cluster', models.ForeignKey(blank=True, null=True, to='data_center.Cluster')),
            ],
            options={
                'verbose_name': 'Virtual server (VM)',
                'verbose_name_plural': 'Virtual servers (VM)',
            },
            bases=(ralph.assets.utils.DNSaaSPublisherMixin, ralph.lib.mixins.models.AdminAbsoluteUrlMixin, 'assets.baseobject', models.Model),
        ),
        migrations.CreateModel(
            name='VirtualServerType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=255, unique=True)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.AddField(
            model_name='virtualserver',
            name='type',
            field=models.ForeignKey(related_name='virtual_servers', to='virtual.VirtualServerType'),
        ),
        migrations.AddField(
            model_name='virtualcomponent',
            name='base_object',
            field=models.ForeignKey(related_name='virtualcomponent_set', to='assets.BaseObject'),
        ),
        migrations.AddField(
            model_name='virtualcomponent',
            name='model',
            field=models.ForeignKey(verbose_name='model', blank=True, null=True, default=None, on_delete=django.db.models.deletion.SET_NULL, to='assets.ComponentModel'),
        ),
        migrations.AddField(
            model_name='cloudproject',
            name='cloudprovider',
            field=models.ForeignKey(to='virtual.CloudProvider'),
        ),
        migrations.AddField(
            model_name='cloudhost',
            name='cloudprovider',
            field=models.ForeignKey(to='virtual.CloudProvider'),
        ),
        migrations.AddField(
            model_name='cloudhost',
            name='hypervisor',
            field=models.ForeignKey(blank=True, null=True, to='data_center.DataCenterAsset'),
        ),
        migrations.AddField(
            model_name='cloudflavor',
            name='cloudprovider',
            field=models.ForeignKey(to='virtual.CloudProvider'),
        ),
    ]
