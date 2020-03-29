# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ralph.lib.mixins.fields
import django.db.models.deletion
import ralph.lib.mixins.models
import ralph.admin.autocomplete


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0001_initial'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseObjectsSupport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
            ],
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Support',
            fields=[
                ('baseobject_ptr', models.OneToOneField(primary_key=True, serialize=False, auto_created=True, parent_link=True, to='assets.BaseObject')),
                ('name', models.CharField(verbose_name='name', max_length=75)),
                ('asset_type', models.PositiveSmallIntegerField(default=4, choices=[(1, 'back office'), (2, 'data center'), (3, 'part'), (4, 'all')])),
                ('contract_id', models.CharField(verbose_name='contract ID', max_length=50)),
                ('description', models.CharField(max_length=100, blank=True)),
                ('price', models.DecimalField(blank=True, null=True, default=0, max_digits=10, decimal_places=2)),
                ('date_from', models.DateField(blank=True, null=True)),
                ('date_to', models.DateField()),
                ('escalation_path', models.CharField(max_length=200, blank=True)),
                ('contract_terms', models.TextField(blank=True)),
                ('sla_type', models.CharField(max_length=200, blank=True)),
                ('status', models.PositiveSmallIntegerField(verbose_name='status', default=1, choices=[(1, 'new')])),
                ('producer', models.CharField(max_length=100, blank=True)),
                ('supplier', models.CharField(max_length=100, blank=True)),
                ('serial_no', models.CharField(verbose_name='serial number', max_length=100, blank=True)),
                ('invoice_no', models.CharField(verbose_name='invoice number', max_length=100, blank=True, db_index=True)),
                ('invoice_date', models.DateField(verbose_name='invoice date', blank=True, null=True)),
                ('period_in_months', models.IntegerField(blank=True, null=True)),
                ('base_objects', models.ManyToManyField(related_name='_support_base_objects_+', to='assets.BaseObject', through='supports.BaseObjectsSupport')),
                ('budget_info', models.ForeignKey(blank=True, null=True, default=None, on_delete=django.db.models.deletion.PROTECT, to='assets.BudgetInfo')),
                ('property_of', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='assets.AssetHolder')),
                ('region', models.ForeignKey(to='accounts.Region')),
            ],
            options={
                'abstract': False,
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, 'assets.baseobject', models.Model, ralph.admin.autocomplete.AutocompleteTooltipMixin),
        ),
        migrations.CreateModel(
            name='SupportType',
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
        migrations.AddField(
            model_name='support',
            name='support_type',
            field=models.ForeignKey(blank=True, null=True, default=None, on_delete=django.db.models.deletion.PROTECT, to='supports.SupportType'),
        ),
        migrations.AddField(
            model_name='baseobjectssupport',
            name='baseobject',
            field=ralph.lib.mixins.fields.BaseObjectForeignKey(verbose_name='Asset', related_name='supports', to='assets.BaseObject'),
        ),
        migrations.AddField(
            model_name='baseobjectssupport',
            name='support',
            field=models.ForeignKey(to='supports.Support'),
        ),
        migrations.AlterUniqueTogether(
            name='baseobjectssupport',
            unique_together=set([('support', 'baseobject')]),
        ),
    ]
