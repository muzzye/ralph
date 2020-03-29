# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import re
import ralph.data_center.models.mixins
import ralph.lib.mixins.models
import ralph.lib.mixins.fields
import ralph.admin.autocomplete
import django.core.validators
import ralph.assets.utils
import ralph.lib.transitions.fields


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Accessory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=255, unique=True)),
            ],
            options={
                'verbose_name': 'accessory',
                'verbose_name_plural': 'accessories',
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='BaseObjectCluster',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('is_master', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Cluster',
            fields=[
                ('baseobject_ptr', models.OneToOneField(primary_key=True, serialize=False, auto_created=True, parent_link=True, to='assets.BaseObject')),
                ('name', models.CharField(verbose_name='name', max_length=255, blank=True, null=True)),
                ('hostname', ralph.lib.mixins.fields.NullableCharField(verbose_name='hostname', max_length=255, unique=True, blank=True, null=True)),
                ('status', ralph.lib.transitions.fields.TransitionField(default=1, choices=[(1, 'in use'), (2, 'for deploy')])),
            ],
            options={
                'abstract': False,
            },
            bases=(ralph.assets.utils.DNSaaSPublisherMixin, ralph.lib.mixins.models.AdminAbsoluteUrlMixin, ralph.data_center.models.mixins.WithManagementIPMixin, 'assets.baseobject', models.Model),
        ),
        migrations.CreateModel(
            name='ClusterType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=255, unique=True)),
                ('show_master_summary', models.BooleanField(default=False, help_text='show master information on cluster page, ex. hostname, model, location etc.')),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Connection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('connection_type', models.PositiveIntegerField(verbose_name='connection type', choices=[(1, 'network connection')])),
            ],
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Database',
            fields=[
                ('baseobject_ptr', models.OneToOneField(primary_key=True, serialize=False, auto_created=True, parent_link=True, to='assets.BaseObject')),
            ],
            options={
                'verbose_name': 'database',
                'verbose_name_plural': 'databases',
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, 'assets.baseobject'),
        ),
        migrations.CreateModel(
            name='DataCenter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=255, unique=True)),
                ('show_on_dashboard', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='DataCenterAsset',
            fields=[
                ('asset_ptr', models.OneToOneField(primary_key=True, serialize=False, auto_created=True, parent_link=True, to='assets.Asset')),
                ('status', ralph.lib.transitions.fields.TransitionField(default=1, choices=[(1, 'new'), (2, 'in use'), (3, 'free'), (4, 'damaged'), (5, 'liquidated'), (6, 'to deploy'), (7, 'cleaned'), (8, 'pre liquidated')])),
                ('position', models.IntegerField(blank=True, null=True)),
                ('orientation', models.PositiveIntegerField(default=1, choices=[(1, 'front'), (2, 'back'), (3, 'middle'), (101, 'left'), (102, 'right')])),
                ('slot_no', models.CharField(verbose_name='slot number', max_length=3, blank=True, null=True, help_text='Fill it if asset is blade server', validators=[django.core.validators.RegexValidator(regex=re.compile('^([1-9][A,B]?|1[0-6][A,B]?)$', 32), message="Slot number should be a number from range 1-16 with an optional postfix 'A' or 'B' (e.g. '16A')", code='invalid_slot_no')])),
                ('firmware_version', models.CharField(verbose_name='firmware version', max_length=256, blank=True, null=True)),
                ('bios_version', models.CharField(verbose_name='BIOS version', max_length=256, blank=True, null=True)),
                ('source', models.PositiveIntegerField(verbose_name='source', blank=True, null=True, db_index=True, choices=[(1, 'shipment'), (2, 'salvaged')])),
                ('delivery_date', models.DateField(blank=True, null=True)),
                ('production_year', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('production_use_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'data center asset',
                'verbose_name_plural': 'data center assets',
            },
            bases=(ralph.assets.utils.DNSaaSPublisherMixin, ralph.data_center.models.mixins.WithManagementIPMixin, ralph.admin.autocomplete.AutocompleteTooltipMixin, 'assets.asset', models.Model),
        ),
        migrations.CreateModel(
            name='DiskShare',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
                ('model_name', models.CharField(verbose_name='model name', max_length=255, blank=True, null=True)),
                ('share_id', models.PositiveIntegerField(verbose_name='share identifier', blank=True, null=True)),
                ('label', models.CharField(verbose_name='name', max_length=255, blank=True, null=True, default=None)),
                ('size', models.PositiveIntegerField(verbose_name='size (MiB)', blank=True, null=True)),
                ('snapshot_size', models.PositiveIntegerField(verbose_name='size for snapshots (MiB)', blank=True, null=True)),
                ('wwn', ralph.lib.mixins.fields.NullableCharField(verbose_name='Volume serial', max_length=33, unique=True)),
                ('full', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'disk share',
                'verbose_name_plural': 'disk shares',
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='DiskShareMount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('volume', models.CharField(verbose_name='volume', max_length=255, blank=True, null=True, default=None)),
                ('size', models.PositiveIntegerField(verbose_name='size (MiB)', blank=True, null=True)),
            ],
            options={
                'verbose_name': 'disk share mount',
                'verbose_name_plural': 'disk share mounts',
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Rack',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=75)),
                ('description', models.CharField(verbose_name='description', max_length=250, blank=True)),
                ('orientation', models.PositiveIntegerField(default=1, choices=[(1, 'top'), (2, 'bottom'), (3, 'left'), (4, 'right')])),
                ('max_u_height', models.IntegerField(default=48)),
                ('visualization_col', models.PositiveIntegerField(verbose_name='column number on visualization grid', default=0)),
                ('visualization_row', models.PositiveIntegerField(verbose_name='row number on visualization grid', default=0)),
                ('require_position', models.BooleanField(default=True, help_text='Uncheck if position is optional for this rack (ex. when rack has warehouse-kind role')),
                ('reverse_ordering', models.BooleanField(verbose_name='RU order top to bottom', default=False, help_text='Check if RU numbers count from top to bottom with position 1 starting at the top of the rack. If unchecked position 1 is at the bottom of the rack')),
            ],
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='RackAccessory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('orientation', models.PositiveIntegerField(default=1, choices=[(1, 'front'), (2, 'back'), (3, 'middle'), (101, 'left'), (102, 'right')])),
                ('position', models.IntegerField(null=True)),
                ('remarks', models.CharField(verbose_name='Additional remarks', max_length=1024, blank=True)),
            ],
            options={
                'verbose_name_plural': 'rack accessories',
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ServerRoom',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=75)),
                ('visualization_cols_num', models.PositiveIntegerField(verbose_name='visualization grid columns number', default=20, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)])),
                ('visualization_rows_num', models.PositiveIntegerField(verbose_name='visualization grid rows number', default=20, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)])),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='VIP',
            fields=[
                ('baseobject_ptr', models.OneToOneField(primary_key=True, serialize=False, auto_created=True, parent_link=True, to='assets.BaseObject')),
                ('name', models.CharField(verbose_name='name', max_length=255)),
                ('port', models.PositiveIntegerField(verbose_name='port', default=0)),
                ('protocol', models.PositiveIntegerField(verbose_name='protocol', default=1, choices=[(1, 'TCP'), (2, 'UDP')])),
            ],
            options={
                'verbose_name': 'VIP',
                'verbose_name_plural': 'VIPs',
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, 'assets.baseobject'),
        ),
        migrations.CreateModel(
            name='DCHost',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, 'assets.baseobject'),
        ),
    ]
