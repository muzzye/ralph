# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ralph.lib.mixins.models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomField',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('attribute_name', models.SlugField(max_length=255, unique=True, editable=False, help_text="field name used in API. It's slugged name of the field")),
                ('type', models.PositiveIntegerField(default=1, choices=[(1, 'string'), (2, 'integer'), (3, 'date'), (4, 'url'), (5, 'choice list')])),
                ('choices', models.TextField(verbose_name='choices', blank=True, null=True, help_text='available choices for `choices list` separated by |')),
                ('default_value', models.CharField(max_length=1000, blank=True, null=True, default='', help_text='for boolean use "true" or "false"')),
                ('use_as_configuration_variable', models.BooleanField(default=False, help_text='When set, this variable will be exposed in API in "configuration_variables" section. You could use this later in configuration management tool like Puppet or Ansible.')),
                ('managing_group', models.ForeignKey(blank=True, null=True, help_text='When set, only members of the specified group will be allowed to set, change or unset values of this custom field for objects.', to='auth.Group')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'abstract': False,
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='CustomFieldValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
                ('value', models.CharField(max_length=1000)),
                ('object_id', models.PositiveIntegerField(db_index=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('custom_field', models.ForeignKey(verbose_name='key', on_delete=django.db.models.deletion.PROTECT, to='custom_fields.CustomField')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='customfieldvalue',
            unique_together=set([('custom_field', 'content_type', 'object_id')]),
        ),
    ]
