# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ralph.lib.mixins.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data_center', '0001_initial'),
        ('assets', '0001_initial'),
        ('networks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='vip',
            name='ip',
            field=models.ForeignKey(to='networks.IPAddress'),
        ),
        migrations.AddField(
            model_name='serverroom',
            name='data_center',
            field=models.ForeignKey(verbose_name='data center', to='data_center.DataCenter'),
        ),
        migrations.AddField(
            model_name='rackaccessory',
            name='accessory',
            field=models.ForeignKey(to='data_center.Accessory'),
        ),
        migrations.AddField(
            model_name='rackaccessory',
            name='rack',
            field=models.ForeignKey(to='data_center.Rack'),
        ),
        migrations.AddField(
            model_name='rack',
            name='accessories',
            field=models.ManyToManyField(to='data_center.Accessory', through='data_center.RackAccessory'),
        ),
        migrations.AddField(
            model_name='rack',
            name='server_room',
            field=models.ForeignKey(verbose_name='server room', null=True, to='data_center.ServerRoom'),
        ),
        migrations.AddField(
            model_name='disksharemount',
            name='asset',
            field=models.ForeignKey(verbose_name='asset', blank=True, null=True, default=None, on_delete=django.db.models.deletion.SET_NULL, to='assets.Asset'),
        ),
        migrations.AddField(
            model_name='disksharemount',
            name='share',
            field=models.ForeignKey(verbose_name='share', to='data_center.DiskShare'),
        ),
        migrations.AddField(
            model_name='diskshare',
            name='base_object',
            field=models.ForeignKey(related_name='diskshare_set', to='assets.BaseObject'),
        ),
        migrations.AddField(
            model_name='diskshare',
            name='model',
            field=models.ForeignKey(verbose_name='model', blank=True, null=True, default=None, on_delete=django.db.models.deletion.SET_NULL, to='assets.ComponentModel'),
        ),
        migrations.AddField(
            model_name='datacenterasset',
            name='connections',
            field=models.ManyToManyField(to='data_center.DataCenterAsset', through='data_center.Connection'),
        ),
        migrations.AddField(
            model_name='datacenterasset',
            name='rack',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='data_center.Rack'),
        ),
        migrations.AddField(
            model_name='connection',
            name='inbound',
            field=models.ForeignKey(verbose_name='connected device', related_name='inbound_connections', on_delete=django.db.models.deletion.PROTECT, to='data_center.DataCenterAsset'),
        ),
        migrations.AddField(
            model_name='connection',
            name='outbound',
            field=models.ForeignKey(verbose_name='connected to device', related_name='outbound_connections', on_delete=django.db.models.deletion.PROTECT, to='data_center.DataCenterAsset'),
        ),
        migrations.AddField(
            model_name='cluster',
            name='base_objects',
            field=models.ManyToManyField(verbose_name='Assigned base objects', related_name='_cluster_base_objects_+', to='assets.BaseObject', through='data_center.BaseObjectCluster'),
        ),
        migrations.AddField(
            model_name='cluster',
            name='type',
            field=models.ForeignKey(to='data_center.ClusterType'),
        ),
        migrations.AddField(
            model_name='baseobjectcluster',
            name='base_object',
            field=ralph.lib.mixins.fields.BaseObjectForeignKey(related_name='clusters', to='assets.BaseObject'),
        ),
        migrations.AddField(
            model_name='baseobjectcluster',
            name='cluster',
            field=models.ForeignKey(to='data_center.Cluster'),
        ),
        migrations.AlterUniqueTogether(
            name='vip',
            unique_together=set([('ip', 'port', 'protocol')]),
        ),
        migrations.AlterUniqueTogether(
            name='rack',
            unique_together=set([('name', 'server_room')]),
        ),
        migrations.AlterUniqueTogether(
            name='disksharemount',
            unique_together=set([('share', 'asset')]),
        ),
        migrations.AlterUniqueTogether(
            name='baseobjectcluster',
            unique_together=set([('cluster', 'base_object')]),
        ),
    ]
