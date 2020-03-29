# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import dj.choices.fields
import ralph.configuration_management.models


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SCMStatusCheck',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
                ('last_checked', models.DateTimeField(verbose_name='Last SCM check')),
                ('check_result', dj.choices.fields.ChoiceField(verbose_name='SCM check result', choices=ralph.configuration_management.models.SCMCheckResult)),
                ('ok', models.BooleanField(default=False, editable=False)),
                ('base_object', models.OneToOneField(to='assets.BaseObject')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
