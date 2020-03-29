# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ralph.lib.mixins.models


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0001_initial'),
        ('taggit', '0002_auto_20150616_2121'),
    ]

    operations = [
        migrations.CreateModel(
            name='SecurityScan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
                ('last_scan_date', models.DateTimeField()),
                ('scan_status', models.PositiveIntegerField(choices=[(1, 'ok'), (2, 'fail'), (3, 'error')])),
                ('next_scan_date', models.DateTimeField()),
                ('details_url', models.URLField(max_length=255, blank=True)),
                ('rescan_url', models.URLField(verbose_name='Rescan url', blank=True)),
                ('is_patched', models.BooleanField(default=False)),
                ('base_object', models.OneToOneField(to='assets.BaseObject')),
                ('tags', ralph.lib.mixins.models.TaggableManager(verbose_name='Tags', blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag')),
            ],
            options={
                'abstract': False,
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Vulnerability',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
                ('name', models.CharField(verbose_name='name', max_length=1024)),
                ('display_name', models.CharField(verbose_name='display name', max_length=1024)),
                ('patch_deadline', models.DateTimeField(blank=True, null=True)),
                ('risk', models.PositiveIntegerField(blank=True, null=True, choices=[(1, 'low'), (2, 'medium'), (3, 'high')])),
                ('external_vulnerability_id', models.IntegerField(unique=True, blank=True, null=True, help_text='Id of vulnerability from external system')),
                ('tags', ralph.lib.mixins.models.TaggableManager(verbose_name='Tags', blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag')),
            ],
            options={
                'abstract': False,
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.AddField(
            model_name='securityscan',
            name='vulnerabilities',
            field=models.ManyToManyField(blank=True, to='security.Vulnerability'),
        ),
    ]
