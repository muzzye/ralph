# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.db.models.deletion
import ralph.lib.mixins.fields
import ralph.lib.mixins.models
import ralph.lib.transitions.fields


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BackOfficeAsset',
            fields=[
                ('asset_ptr', models.OneToOneField(primary_key=True, serialize=False, auto_created=True, parent_link=True, to='assets.Asset')),
                ('location', models.CharField(max_length=128, blank=True, null=True)),
                ('purchase_order', models.CharField(max_length=50, blank=True, null=True)),
                ('loan_end_date', models.DateField(verbose_name='Loan end date', blank=True, null=True, default=None)),
                ('status', ralph.lib.transitions.fields.TransitionField(default=1, choices=[(1, 'new'), (2, 'in progress'), (3, 'waiting for release'), (4, 'in use'), (5, 'loan'), (6, 'damaged'), (7, 'liquidated'), (8, 'in service'), (9, 'installed'), (10, 'free'), (11, 'reserved'), (12, 'sale'), (13, 'loan in progress'), (14, 'return in progress')])),
                ('imei', ralph.lib.mixins.fields.NullableCharField(verbose_name='IMEI', max_length=18, unique=True, blank=True, null=True)),
                ('imei2', ralph.lib.mixins.fields.NullableCharField(verbose_name='IMEI 2', max_length=18, unique=True, blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Back Office Asset',
                'verbose_name_plural': 'Back Office Assets',
            },
            bases=('assets.asset', models.Model),
        ),
        migrations.CreateModel(
            name='OfficeInfrastructure',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=255, unique=True)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
            ],
            options={
                'verbose_name': 'Office Infrastructure',
                'verbose_name_plural': 'Office Infrastructures',
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Warehouse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=255, unique=True)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
                ('stocktaking_enabled', models.BooleanField(default=False)),
                ('stocktaking_tag_suffix', models.CharField(max_length=8, blank=True, default='')),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.AddField(
            model_name='backofficeasset',
            name='office_infrastructure',
            field=models.ForeignKey(blank=True, null=True, to='back_office.OfficeInfrastructure'),
        ),
        migrations.AddField(
            model_name='backofficeasset',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, related_name='assets_as_owner', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='backofficeasset',
            name='region',
            field=models.ForeignKey(to='accounts.Region'),
        ),
        migrations.AddField(
            model_name='backofficeasset',
            name='user',
            field=models.ForeignKey(blank=True, null=True, related_name='assets_as_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='backofficeasset',
            name='warehouse',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='back_office.Warehouse'),
        ),
    ]
