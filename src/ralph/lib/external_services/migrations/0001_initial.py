# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_extensions.db.fields.json
import ralph.lib.mixins.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ('username', ralph.lib.mixins.fields.NullableCharField(max_length=200, blank=True, null=True)),
                ('service_name', models.CharField(max_length=200)),
                ('_dumped_params', django_extensions.db.fields.json.JSONField(default=dict)),
                ('status', models.PositiveIntegerField(verbose_name='job status', default=1, choices=[(1, 'queued'), (2, 'finished'), (3, 'failed'), (4, 'started'), (5, 'frozen'), (6, 'killed')])),
            ],
        ),
    ]
