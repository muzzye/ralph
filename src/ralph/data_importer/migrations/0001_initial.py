# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImportedObjects',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
                ('object_pk', models.IntegerField(db_index=True)),
                ('old_object_pk', models.CharField(max_length=255, db_index=True)),
                ('old_ci_uid', models.CharField(max_length=255, blank=True, null=True, db_index=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='importedobjects',
            unique_together=set([('content_type', 'object_pk'), ('content_type', 'old_object_pk')]),
        ),
    ]
