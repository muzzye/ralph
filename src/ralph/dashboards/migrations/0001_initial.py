# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_extensions.db.fields.json
import ralph.lib.mixins.models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dashboard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=255, unique=True)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('description', models.CharField(verbose_name='description', max_length=250, blank=True)),
                ('interval', models.PositiveSmallIntegerField(default=60)),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Graph',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=255, unique=True)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
                ('description', models.CharField(verbose_name='description', max_length=250, blank=True)),
                ('aggregate_type', models.PositiveIntegerField(choices=[(1, 'Count'), (2, 'Count with zeros'), (3, 'Max'), (4, 'Sum'), (5, 'Sum with zeros'), (6, 'Sum boolean values'), (7, 'Sum negated boolean values'), (8, 'Ratio')])),
                ('chart_type', models.PositiveIntegerField(choices=[(1, 'Vertical Bar'), (2, 'Horizontal Bar'), (3, 'Pie Chart')])),
                ('params', django_extensions.db.fields.json.JSONField(blank=True, default=dict)),
                ('active', models.BooleanField(default=True)),
                ('push_to_statsd', models.BooleanField(default=False, help_text="Push graph's data to statsd.")),
                ('model', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.AddField(
            model_name='dashboard',
            name='graphs',
            field=models.ManyToManyField(blank=True, to='dashboards.Graph'),
        ),
    ]
