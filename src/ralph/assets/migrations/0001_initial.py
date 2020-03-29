# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import re
import ralph.lib.mixins.models
import ralph.admin.autocomplete
import ralph.lib.mixins.fields
import django.core.validators
import mptt.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('taggit', '0002_auto_20150616_2121'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssetHolder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=75)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='AssetLastHostname',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('prefix', models.CharField(max_length=30, db_index=True)),
                ('counter', models.PositiveIntegerField(default=1)),
                ('postfix', models.CharField(max_length=30, db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='AssetModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=75)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
                ('type', models.PositiveIntegerField(verbose_name='type', choices=[(1, 'back office'), (2, 'data center'), (3, 'part'), (4, 'all')])),
                ('power_consumption', models.PositiveIntegerField(verbose_name='Power consumption', default=0)),
                ('height_of_device', models.FloatField(verbose_name='Height of device', default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('cores_count', models.PositiveIntegerField(verbose_name='Cores count', default=0)),
                ('visualization_layout_front', models.PositiveIntegerField(verbose_name='visualization layout of front side', blank=True, default=1, choices=[(1, 'N/A'), (2, '1 row x 2 columns'), (3, '2 rows x 8 columns'), (4, '2 rows x 16 columns (A/B)'), (5, '4 rows x 2 columns'), (6, '2 rows x 4 columns'), (7, '2 rows x 2 columns'), (8, '1 rows x 14 columns'), (9, '2 rows x 1 columns')])),
                ('visualization_layout_back', models.PositiveIntegerField(verbose_name='visualization layout of back side', blank=True, default=1, choices=[(1, 'N/A'), (2, '1 row x 2 columns'), (3, '2 rows x 8 columns'), (4, '2 rows x 16 columns (A/B)'), (5, '4 rows x 2 columns'), (6, '2 rows x 4 columns'), (7, '2 rows x 2 columns'), (8, '1 rows x 14 columns'), (9, '2 rows x 1 columns')])),
                ('has_parent', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'model',
                'verbose_name_plural': 'models',
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='BaseObject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
                ('remarks', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BudgetInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=255, unique=True)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
            ],
            options={
                'verbose_name': 'Budget info',
                'verbose_name_plural': 'Budgets info',
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='BusinessSegment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=255, unique=True)),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=75)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
                ('code', models.CharField(max_length=4, blank=True, default='')),
                ('imei_required', models.BooleanField(default=False)),
                ('allow_deployment', models.BooleanField(default=False)),
                ('show_buyout_date', models.BooleanField(default=False)),
                ('default_depreciation_rate', models.DecimalField(blank=True, default=25, help_text='This value is in percentage. For example value: "100" means it depreciates during a year. Value: "25" means it depreciates during 4 years, and so on... .', max_digits=5, decimal_places=2)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, related_name='children', to='assets.Category')),
            ],
            options={
                'verbose_name': 'category',
                'verbose_name_plural': 'categories',
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ComponentModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=255, unique=True)),
                ('speed', models.PositiveIntegerField(verbose_name='speed (MHz)', blank=True, default=0)),
                ('cores', models.PositiveIntegerField(verbose_name='number of cores', blank=True, default=0)),
                ('size', models.PositiveIntegerField(verbose_name='size (MiB)', blank=True, default=0)),
                ('type', models.PositiveIntegerField(verbose_name='component type', default=8, choices=[(1, 'processor'), (2, 'memory'), (3, 'disk drive'), (4, 'ethernet card'), (5, 'expansion card'), (6, 'fibre channel card'), (7, 'disk share'), (8, 'unknown'), (9, 'management'), (10, 'power module'), (11, 'cooling device'), (12, 'media tray'), (13, 'chassis'), (14, 'backup'), (15, 'software'), (16, 'operating system')])),
                ('family', models.CharField(max_length=128, blank=True, default='')),
            ],
            options={
                'verbose_name': 'component model',
                'verbose_name_plural': 'component models',
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, ralph.admin.autocomplete.AutocompleteTooltipMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ConfigurationModule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
                ('name', models.CharField(verbose_name='name', max_length=255, help_text='module name (ex. directory name in puppet)', validators=[django.core.validators.RegexValidator(regex='\\w+')])),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(verbose_name='parent module', blank=True, null=True, default=None, related_name='children_modules', to='assets.ConfigurationModule')),
                ('support_team', models.ForeignKey(verbose_name='team', blank=True, null=True, default=None, on_delete=django.db.models.deletion.SET_NULL, to='accounts.Team')),
            ],
            options={
                'verbose_name': 'configuration module',
                'ordering': ('parent__name', 'name'),
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Disk',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
                ('model_name', models.CharField(verbose_name='model name', max_length=255, blank=True, null=True)),
                ('size', models.PositiveIntegerField(verbose_name='size (GiB)')),
                ('serial_number', models.CharField(verbose_name='serial number', max_length=255, blank=True, null=True)),
                ('slot', models.PositiveIntegerField(verbose_name='slot number', blank=True, null=True)),
                ('firmware_version', models.CharField(verbose_name='firmware version', max_length=255, blank=True, null=True)),
            ],
            options={
                'verbose_name': 'disk',
                'verbose_name_plural': 'disks',
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Environment',
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
        migrations.CreateModel(
            name='Ethernet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
                ('model_name', models.CharField(verbose_name='model name', max_length=255, blank=True, null=True)),
                ('label', ralph.lib.mixins.fields.NullableCharField(verbose_name='label', max_length=255, blank=True, null=True)),
                ('mac', ralph.lib.mixins.fields.MACAddressField(verbose_name='MAC address', unique=True, blank=True, null=True, validators=[django.core.validators.RegexValidator(regex=re.compile('^\\s*([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}\\s*$', 32), message="'%(value)s' is not a valid MAC address.")])),
                ('speed', models.PositiveIntegerField(verbose_name='speed', default=11, choices=[(1, '10 Mbps'), (2, '100 Mbps'), (3, '1 Gbps'), (4, '10 Gbps'), (5, '40 Gbps'), (6, '100 Gbps'), (11, 'unknown speed')])),
                ('firmware_version', models.CharField(verbose_name='firmware version', max_length=255, blank=True, null=True)),
            ],
            options={
                'verbose_name': 'ethernet',
                'verbose_name_plural': 'ethernets',
                'ordering': ('base_object', 'mac'),
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='FibreChannelCard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
                ('model_name', models.CharField(verbose_name='model name', max_length=255, blank=True, null=True)),
                ('firmware_version', models.CharField(verbose_name='firmware version', max_length=255, blank=True, null=True)),
                ('speed', models.PositiveIntegerField(verbose_name='speed', default=11, choices=[(1, '1 Gbit'), (2, '2 Gbit'), (3, '4 Gbit'), (4, '8 Gbit'), (5, '16 Gbit'), (6, '32 Gbit'), (11, 'unknown speed')])),
                ('wwn', ralph.lib.mixins.fields.NullableCharField(verbose_name='WWN', max_length=255, unique=True, blank=True, null=True, default=None)),
            ],
            options={
                'verbose_name': 'fibre channel card',
                'verbose_name_plural': 'fibre channel cards',
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='GenericComponent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
                ('model_name', models.CharField(verbose_name='model name', max_length=255, blank=True, null=True)),
                ('label', models.CharField(verbose_name='label', max_length=255, blank=True, null=True, default=None)),
                ('sn', ralph.lib.mixins.fields.NullableCharField(verbose_name='vendor SN', max_length=255, unique=True, blank=True, null=True, default=None)),
            ],
            options={
                'verbose_name': 'generic component',
                'verbose_name_plural': 'generic components',
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Manufacturer',
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
        migrations.CreateModel(
            name='ManufacturerKind',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=255, unique=True)),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Memory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
                ('model_name', models.CharField(verbose_name='model name', max_length=255, blank=True, null=True)),
                ('size', models.PositiveIntegerField(verbose_name='size (MiB)')),
                ('speed', models.PositiveIntegerField(verbose_name='speed (MHz)', blank=True, null=True)),
            ],
            options={
                'verbose_name': 'memory',
                'verbose_name_plural': 'memory',
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Processor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
                ('model_name', models.CharField(verbose_name='model name', max_length=255, blank=True, null=True)),
                ('speed', models.PositiveIntegerField(verbose_name='speed (MHz)', blank=True, null=True)),
                ('cores', models.PositiveIntegerField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'processor',
                'verbose_name_plural': 'processors',
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ProfitCenter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=255, unique=True)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=255, unique=True)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('uid', ralph.lib.mixins.fields.NullableCharField(max_length=40, unique=True, blank=True, null=True)),
                ('cost_center', models.CharField(max_length=100, blank=True)),
                ('business_owners', models.ManyToManyField(blank=True, related_name='services_business_owner', to=settings.AUTH_USER_MODEL)),
                ('business_segment', models.ForeignKey(blank=True, null=True, to='assets.BusinessSegment')),
                ('profit_center', models.ForeignKey(blank=True, null=True, to='assets.ProfitCenter')),
                ('support_team', models.ForeignKey(blank=True, null=True, related_name='services', to='accounts.Team')),
                ('technical_owners', models.ManyToManyField(blank=True, related_name='services_technical_owner', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('baseobject_ptr', models.OneToOneField(primary_key=True, serialize=False, auto_created=True, parent_link=True, to='assets.BaseObject')),
                ('hostname', ralph.lib.mixins.fields.NullableCharField(verbose_name='hostname', max_length=255, blank=True, null=True, default=None)),
                ('sn', ralph.lib.mixins.fields.NullableCharField(verbose_name='SN', max_length=200, unique=True, blank=True, null=True)),
                ('barcode', ralph.lib.mixins.fields.NullableCharField(verbose_name='barcode', max_length=200, unique=True, blank=True, null=True, default=None)),
                ('niw', ralph.lib.mixins.fields.NullableCharField(verbose_name='inventory number', max_length=200, blank=True, null=True, default=None)),
                ('required_support', models.BooleanField(default=False)),
                ('order_no', models.CharField(verbose_name='order number', max_length=50, blank=True, null=True)),
                ('invoice_no', models.CharField(verbose_name='invoice number', max_length=128, blank=True, null=True, db_index=True)),
                ('invoice_date', models.DateField(blank=True, null=True)),
                ('price', models.DecimalField(blank=True, null=True, default=0, max_digits=10, decimal_places=2)),
                ('provider', models.CharField(max_length=100, blank=True, null=True)),
                ('depreciation_rate', models.DecimalField(blank=True, default=25, help_text='This value is in percentage. For example value: "100" means it depreciates during a year. Value: "25" means it depreciates during 4 years, and so on... .', max_digits=5, decimal_places=2)),
                ('force_depreciation', models.BooleanField(default=False, help_text='Check if you no longer want to bill for this asset')),
                ('depreciation_end_date', models.DateField(blank=True, null=True)),
                ('buyout_date', models.DateField(blank=True, null=True, db_index=True)),
                ('task_url', models.URLField(max_length=2048, blank=True, null=True, help_text='External workflow system URL')),
                ('start_usage', models.DateField(blank=True, null=True, help_text='Fill it if date of first usage is different then date of creation')),
                ('budget_info', models.ForeignKey(blank=True, null=True, default=None, on_delete=django.db.models.deletion.PROTECT, to='assets.BudgetInfo')),
            ],
            options={
                'abstract': False,
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, 'assets.baseobject'),
        ),
        migrations.CreateModel(
            name='ConfigurationClass',
            fields=[
                ('baseobject_ptr', models.OneToOneField(primary_key=True, serialize=False, auto_created=True, parent_link=True, to='assets.BaseObject')),
                ('class_name', models.CharField(verbose_name='class name', max_length=255, help_text='ex. puppet class', validators=[django.core.validators.RegexValidator(regex='\\w+')])),
                ('path', models.CharField(verbose_name='path', max_length=511, blank=True, default='', editable=False, help_text='path is constructed from name of module and name of class')),
            ],
            options={
                'verbose_name': 'configuration class',
                'ordering': ('path',),
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, 'assets.baseobject'),
        ),
        migrations.CreateModel(
            name='ServiceEnvironment',
            fields=[
                ('baseobject_ptr', models.OneToOneField(primary_key=True, serialize=False, auto_created=True, parent_link=True, to='assets.BaseObject')),
                ('environment', models.ForeignKey(to='assets.Environment')),
                ('service', models.ForeignKey(to='assets.Service')),
            ],
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, ralph.admin.autocomplete.AutocompleteTooltipMixin, 'assets.baseobject'),
        ),
        migrations.AddField(
            model_name='processor',
            name='base_object',
            field=models.ForeignKey(related_name='processor_set', to='assets.BaseObject'),
        ),
        migrations.AddField(
            model_name='processor',
            name='model',
            field=models.ForeignKey(verbose_name='model', blank=True, null=True, default=None, on_delete=django.db.models.deletion.SET_NULL, to='assets.ComponentModel'),
        ),
        migrations.AddField(
            model_name='memory',
            name='base_object',
            field=models.ForeignKey(related_name='memory_set', to='assets.BaseObject'),
        ),
        migrations.AddField(
            model_name='memory',
            name='model',
            field=models.ForeignKey(verbose_name='model', blank=True, null=True, default=None, on_delete=django.db.models.deletion.SET_NULL, to='assets.ComponentModel'),
        ),
        migrations.AddField(
            model_name='manufacturer',
            name='manufacturer_kind',
            field=models.ForeignKey(verbose_name='manufacturer kind', blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='assets.ManufacturerKind'),
        ),
        migrations.AddField(
            model_name='genericcomponent',
            name='base_object',
            field=models.ForeignKey(related_name='genericcomponent_set', to='assets.BaseObject'),
        ),
        migrations.AddField(
            model_name='genericcomponent',
            name='model',
            field=models.ForeignKey(verbose_name='model', blank=True, null=True, default=None, on_delete=django.db.models.deletion.SET_NULL, to='assets.ComponentModel'),
        ),
        migrations.AddField(
            model_name='fibrechannelcard',
            name='base_object',
            field=models.ForeignKey(related_name='fibrechannelcard_set', to='assets.BaseObject'),
        ),
        migrations.AddField(
            model_name='fibrechannelcard',
            name='model',
            field=models.ForeignKey(verbose_name='model', blank=True, null=True, default=None, on_delete=django.db.models.deletion.SET_NULL, to='assets.ComponentModel'),
        ),
        migrations.AddField(
            model_name='ethernet',
            name='base_object',
            field=models.ForeignKey(related_name='ethernet_set', to='assets.BaseObject'),
        ),
        migrations.AddField(
            model_name='ethernet',
            name='model',
            field=models.ForeignKey(verbose_name='model', blank=True, null=True, default=None, on_delete=django.db.models.deletion.SET_NULL, to='assets.ComponentModel'),
        ),
        migrations.AddField(
            model_name='disk',
            name='base_object',
            field=models.ForeignKey(related_name='disk_set', to='assets.BaseObject'),
        ),
        migrations.AddField(
            model_name='disk',
            name='model',
            field=models.ForeignKey(verbose_name='model', blank=True, null=True, default=None, on_delete=django.db.models.deletion.SET_NULL, to='assets.ComponentModel'),
        ),
        migrations.AlterUniqueTogether(
            name='componentmodel',
            unique_together=set([('speed', 'cores', 'size', 'type', 'family')]),
        ),
        migrations.AddField(
            model_name='baseobject',
            name='content_type',
            field=models.ForeignKey(blank=True, null=True, to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='baseobject',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, related_name='children', on_delete=django.db.models.deletion.SET_NULL, to='assets.BaseObject'),
        ),
        migrations.AddField(
            model_name='baseobject',
            name='tags',
            field=ralph.lib.mixins.models.TaggableManager(verbose_name='Tags', blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag'),
        ),
        migrations.AddField(
            model_name='assetmodel',
            name='category',
            field=mptt.fields.TreeForeignKey(null=True, related_name='models', to='assets.Category'),
        ),
        migrations.AddField(
            model_name='assetmodel',
            name='manufacturer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='assets.Manufacturer'),
        ),
        migrations.AlterUniqueTogether(
            name='assetlasthostname',
            unique_together=set([('prefix', 'postfix')]),
        ),
        migrations.AddField(
            model_name='service',
            name='environments',
            field=models.ManyToManyField(to='assets.Environment', through='assets.ServiceEnvironment'),
        ),
        migrations.AlterUniqueTogether(
            name='configurationmodule',
            unique_together=set([('parent', 'name')]),
        ),
        migrations.AddField(
            model_name='configurationclass',
            name='module',
            field=models.ForeignKey(related_name='configuration_classes', to='assets.ConfigurationModule'),
        ),
        migrations.AddField(
            model_name='baseobject',
            name='configuration_path',
            field=models.ForeignKey(verbose_name='configuration path', blank=True, null=True, help_text='path to configuration for this object, for example path to puppet class', on_delete=django.db.models.deletion.PROTECT, to='assets.ConfigurationClass'),
        ),
        migrations.AddField(
            model_name='baseobject',
            name='service_env',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='assets.ServiceEnvironment'),
        ),
        migrations.AddField(
            model_name='asset',
            name='model',
            field=models.ForeignKey(related_name='assets', on_delete=django.db.models.deletion.PROTECT, to='assets.AssetModel'),
        ),
        migrations.AddField(
            model_name='asset',
            name='property_of',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='assets.AssetHolder'),
        ),
        migrations.AlterUniqueTogether(
            name='serviceenvironment',
            unique_together=set([('service', 'environment')]),
        ),
        migrations.AlterUniqueTogether(
            name='configurationclass',
            unique_together=set([('module', 'class_name')]),
        ),
    ]
