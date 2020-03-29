# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_extensions.db.fields.json
from django.conf import settings
import django.db.models.deletion
import ralph.lib.mixins.fields
import ralph.lib.mixins.models


class Migration(migrations.Migration):

    dependencies = [
        ('external_services', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
        ('attachments', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=50)),
                ('content_type', models.ManyToManyField(to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Transition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=50)),
                ('run_asynchronously', models.BooleanField(default=False, help_text='Run this transition in the background (this could be enforced if you choose at least one asynchronous action)')),
                ('async_service_name', models.CharField(max_length=100, blank=True, null=True, default='ASYNC_TRANSITIONS', help_text='Name of asynchronous (internal) service to run this transition. Fill this field only if you want to run this transition in the background.')),
                ('source', django_extensions.db.fields.json.JSONField(default=dict)),
                ('target', models.CharField(max_length=50)),
                ('template_name', models.CharField(max_length=255, blank=True, default='')),
                ('success_url', ralph.lib.mixins.fields.NullableCharField(max_length=255, blank=True, null=True, default=None)),
                ('actions', models.ManyToManyField(to='transitions.Action')),
            ],
        ),
        migrations.CreateModel(
            name='TransitionJob',
            fields=[
                ('job_ptr', models.OneToOneField(primary_key=True, serialize=False, auto_created=True, parent_link=True, to='external_services.Job')),
                ('object_id', models.CharField(max_length=200)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contenttypes.ContentType')),
                ('transition', models.ForeignKey(related_name='jobs', to='transitions.Transition')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'abstract': False,
            },
            bases=('external_services.job',),
        ),
        migrations.CreateModel(
            name='TransitionJobAction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
                ('action_name', models.CharField(max_length=50)),
                ('status', models.PositiveIntegerField(verbose_name='transition action status', default=1, choices=[(1, 'started'), (2, 'finished'), (3, 'failed')])),
                ('transition_job', models.ForeignKey(related_name='transition_job_actions', on_delete=django.db.models.deletion.PROTECT, to='transitions.TransitionJob')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TransitionModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('field_name', models.CharField(max_length=50)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='TransitionsHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
                ('transition_name', models.CharField(max_length=255)),
                ('source', models.CharField(max_length=50, blank=True, null=True)),
                ('target', models.CharField(max_length=50, blank=True, null=True)),
                ('object_id', models.IntegerField(db_index=True)),
                ('kwargs', django_extensions.db.fields.json.JSONField(default=dict)),
                ('actions', django_extensions.db.fields.json.JSONField(default=dict)),
                ('attachments', models.ManyToManyField(to='attachments.Attachment')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('logged_user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='transition',
            name='model',
            field=models.ForeignKey(to='transitions.TransitionModel'),
        ),
        migrations.AlterUniqueTogether(
            name='transitionmodel',
            unique_together=set([('content_type', 'field_name')]),
        ),
        migrations.AlterUniqueTogether(
            name='transition',
            unique_together=set([('name', 'model')]),
        ),
    ]
