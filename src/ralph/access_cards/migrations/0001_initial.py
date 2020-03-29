# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import mptt.fields
import ralph.lib.mixins.models
import ralph.lib.transitions.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AccessCard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
                ('visual_number', models.CharField(max_length=255, unique=True, help_text='Number visible on the access card')),
                ('system_number', models.CharField(max_length=255, unique=True, help_text='Internal number in the access system')),
                ('issue_date', models.DateField(blank=True, null=True, help_text='Date of issue to the User')),
                ('notes', models.TextField(blank=True, null=True, help_text='Optional notes')),
                ('status', ralph.lib.transitions.fields.TransitionField(default=1, choices=[(1, 'new'), (2, 'in progress'), (3, 'lost'), (4, 'damaged'), (5, 'in use'), (6, 'free'), (7, 'return in progres'), (8, 'liquidated')], help_text='Access card status')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'abstract': False,
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='AccessZone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=255)),
                ('description', models.TextField(blank=True, null=True, help_text='Optional description')),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, related_name='children', to='access_cards.AccessZone')),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.AddField(
            model_name='accesscard',
            name='access_zones',
            field=mptt.fields.TreeManyToManyField(blank=True, related_name='access_cards', to='access_cards.AccessZone'),
        ),
    ]
