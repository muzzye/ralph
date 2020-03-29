# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ralph.lib.mixins.models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SSLCertificate',
            fields=[
                ('baseobject_ptr', models.OneToOneField(primary_key=True, serialize=False, auto_created=True, parent_link=True, to='assets.BaseObject')),
                ('name', models.CharField(verbose_name='certificate name', max_length=255, help_text='Full certificate name')),
                ('domain_ssl', models.CharField(verbose_name='domain name', max_length=255, blank=True, help_text='Full domain name')),
                ('certificate_type', models.PositiveIntegerField(default=2, choices=[(1, 'EV'), (2, 'OV'), (3, 'DV'), (4, 'Wildcard'), (5, 'Multisan'), (6, 'CA ENT')])),
                ('date_from', models.DateField(blank=True, null=True)),
                ('date_to', models.DateField()),
                ('san', models.TextField(blank=True, help_text='All Subject Alternative Names')),
                ('price', models.DecimalField(blank=True, null=True, default=0, max_digits=10, decimal_places=2)),
                ('issued_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='assets.Manufacturer')),
            ],
            options={
                'abstract': False,
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, 'assets.baseobject'),
        ),
    ]
