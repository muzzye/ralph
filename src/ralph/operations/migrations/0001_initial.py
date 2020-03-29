# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import mptt.fields
import django.db.models.deletion
import ralph.lib.mixins.fields
import ralph.lib.mixins.models


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('taggit', '0002_auto_20150616_2121'),
    ]

    operations = [
        migrations.CreateModel(
            name='Operation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('title', models.CharField(verbose_name='title', max_length=350)),
                ('description', models.TextField(verbose_name='description', blank=True, null=True)),
                ('ticket_id', ralph.lib.mixins.fields.TicketIdField(verbose_name='ticket id', max_length=200, unique=True, blank=True, null=True, help_text='External system ticket identifier')),
                ('created_date', models.DateTimeField(verbose_name='created date', blank=True, null=True)),
                ('update_date', models.DateTimeField(verbose_name='updated date', blank=True, null=True)),
                ('resolved_date', models.DateTimeField(verbose_name='resolved date', blank=True, null=True)),
                ('assignee', models.ForeignKey(verbose_name='assignee', blank=True, null=True, related_name='operations', on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('base_objects', models.ManyToManyField(verbose_name='objects', blank=True, related_name='operations', to='assets.BaseObject')),
                ('reporter', models.ForeignKey(verbose_name='reporter', blank=True, null=True, related_name='reported_operations', on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='OperationStatus',
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
            name='OperationType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=255, unique=True)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, related_name='children', to='operations.OperationType')),
            ],
            options={
                'abstract': False,
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.AddField(
            model_name='operation',
            name='status',
            field=models.ForeignKey(verbose_name='status', on_delete=django.db.models.deletion.PROTECT, to='operations.OperationStatus'),
        ),
        migrations.AddField(
            model_name='operation',
            name='tags',
            field=ralph.lib.mixins.models.TaggableManager(verbose_name='Tags', blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag'),
        ),
        migrations.AddField(
            model_name='operation',
            name='type',
            field=mptt.fields.TreeForeignKey(verbose_name='type', to='operations.OperationType'),
        ),
        migrations.CreateModel(
            name='Change',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('operations.operation',),
        ),
        migrations.CreateModel(
            name='Failure',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('operations.operation',),
        ),
        migrations.CreateModel(
            name='Incident',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('operations.operation',),
        ),
        migrations.CreateModel(
            name='Problem',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('operations.operation',),
        ),
    ]
