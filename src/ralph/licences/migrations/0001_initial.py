# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import ralph.lib.mixins.fields
import django.db.models.deletion
import ralph.lib.mixins.models


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('back_office', '0001_initial'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseObjectLicence',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('quantity', models.PositiveIntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='Licence',
            fields=[
                ('baseobject_ptr', models.OneToOneField(primary_key=True, serialize=False, auto_created=True, parent_link=True, to='assets.BaseObject')),
                ('number_bought', models.IntegerField(verbose_name='number of purchased items')),
                ('sn', models.TextField(verbose_name='SN / key', blank=True, null=True)),
                ('niw', models.CharField(verbose_name='inventory number', max_length=200, unique=True, default='N/A')),
                ('invoice_date', models.DateField(verbose_name='invoice date', blank=True, null=True)),
                ('valid_thru', models.DateField(blank=True, null=True, help_text='Leave blank if this licence is perpetual')),
                ('order_no', models.CharField(max_length=50, blank=True, null=True)),
                ('price', models.DecimalField(blank=True, null=True, default=0, max_digits=10, decimal_places=2)),
                ('depreciation_rate', models.DecimalField(blank=True, null=True, default=50, help_text='This value is in percentage. For example value: "100" means it depreciates during a year. Value: "25" means it depreciates during 4 years, and so on... .', max_digits=5, decimal_places=2)),
                ('accounting_id', models.CharField(max_length=200, blank=True, null=True, help_text='Any value to help your accounting department identify this licence')),
                ('provider', models.CharField(max_length=100, blank=True, null=True)),
                ('invoice_no', models.CharField(max_length=128, blank=True, null=True, db_index=True)),
                ('license_details', models.CharField(verbose_name='license details', max_length=1024, blank=True, default='')),
                ('start_usage', models.DateField(blank=True, null=True, help_text='Fill it if date of first usage is different then date of creation')),
                ('base_objects', models.ManyToManyField(verbose_name='assigned base objects', related_name='_licence_base_objects_+', to='assets.BaseObject', through='licences.BaseObjectLicence')),
                ('budget_info', models.ForeignKey(blank=True, null=True, default=None, on_delete=django.db.models.deletion.PROTECT, to='assets.BudgetInfo')),
            ],
            options={
                'abstract': False,
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, 'assets.baseobject', models.Model),
        ),
        migrations.CreateModel(
            name='LicenceType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=255, unique=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='LicenceUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('licence', models.ForeignKey(to='licences.Licence')),
                ('user', models.ForeignKey(related_name='licences', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Software',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=255, unique=True)),
                ('asset_type', models.PositiveSmallIntegerField(default=4, choices=[(1, 'back office'), (2, 'data center'), (3, 'part'), (4, 'all')])),
            ],
            options={
                'verbose_name_plural': 'software categories',
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.AddField(
            model_name='licence',
            name='licence_type',
            field=models.ForeignKey(help_text="Should be like 'per processor' or 'per machine' and so on. ", on_delete=django.db.models.deletion.PROTECT, to='licences.LicenceType'),
        ),
        migrations.AddField(
            model_name='licence',
            name='manufacturer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='assets.Manufacturer'),
        ),
        migrations.AddField(
            model_name='licence',
            name='office_infrastructure',
            field=models.ForeignKey(blank=True, null=True, to='back_office.OfficeInfrastructure'),
        ),
        migrations.AddField(
            model_name='licence',
            name='property_of',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='assets.AssetHolder'),
        ),
        migrations.AddField(
            model_name='licence',
            name='region',
            field=models.ForeignKey(to='accounts.Region'),
        ),
        migrations.AddField(
            model_name='licence',
            name='software',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='licences.Software'),
        ),
        migrations.AddField(
            model_name='licence',
            name='users',
            field=models.ManyToManyField(related_name='_licence_users_+', to=settings.AUTH_USER_MODEL, through='licences.LicenceUser'),
        ),
        migrations.AddField(
            model_name='baseobjectlicence',
            name='base_object',
            field=ralph.lib.mixins.fields.BaseObjectForeignKey(verbose_name='Asset', related_name='licences', to='assets.BaseObject'),
        ),
        migrations.AddField(
            model_name='baseobjectlicence',
            name='licence',
            field=models.ForeignKey(to='licences.Licence'),
        ),
        migrations.AlterUniqueTogether(
            name='licenceuser',
            unique_together=set([('licence', 'user')]),
        ),
        migrations.AlterUniqueTogether(
            name='baseobjectlicence',
            unique_together=set([('licence', 'base_object')]),
        ),
    ]
