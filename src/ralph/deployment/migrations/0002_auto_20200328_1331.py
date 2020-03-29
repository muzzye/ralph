# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ralph.lib.mixins.fields
import ralph.deployment.models
import ralph.lib.mixins.models


class Migration(migrations.Migration):

    dependencies = [
        ('deployment', '0001_initial'),
        ('transitions', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Deployment',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, 'transitions.transitionjob'),
        ),
        migrations.CreateModel(
            name='PrebootConfiguration',
            fields=[
                ('prebootitem_ptr', models.OneToOneField(primary_key=True, serialize=False, auto_created=True, parent_link=True, to='deployment.PrebootItem')),
                ('type', models.PositiveIntegerField(verbose_name='type', default=41, choices=[(41, 'ipxe'), (42, 'kickstart'), (43, 'preseed'), (44, 'script')])),
                ('configuration', ralph.lib.mixins.fields.NUMP(models.TextField(blank=True), fields_to_ignore=('help_text', 'verbose_name'))),
            ],
            options={
                'verbose_name': 'preboot configuration',
                'verbose_name_plural': 'preboot configuration',
            },
            bases=('deployment.prebootitem',),
        ),
        migrations.CreateModel(
            name='PrebootFile',
            fields=[
                ('prebootitem_ptr', models.OneToOneField(primary_key=True, serialize=False, auto_created=True, parent_link=True, to='deployment.PrebootItem')),
                ('type', models.PositiveIntegerField(verbose_name='type', default=1, choices=[(1, 'kernel'), (2, 'initrd'), (3, 'netboot')])),
                ('file', models.FileField(verbose_name='file', blank=True, null=True, default=None, upload_to=ralph.deployment.models.preboot_file_name)),
            ],
            options={
                'verbose_name': 'preboot file',
                'verbose_name_plural': 'preboot files',
            },
            bases=('deployment.prebootitem',),
        ),
        migrations.AddField(
            model_name='prebootitem',
            name='content_type',
            field=models.ForeignKey(blank=True, null=True, to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='preboot',
            name='items',
            field=models.ManyToManyField(verbose_name='files', blank=True, to='deployment.PrebootItem'),
        ),
    ]
