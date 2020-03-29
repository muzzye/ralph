# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import ralph.lib.mixins.models


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DNSProvider',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=255, unique=True)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('baseobject_ptr', models.OneToOneField(primary_key=True, serialize=False, auto_created=True, parent_link=True, to='assets.BaseObject')),
                ('name', models.CharField(verbose_name='domain name', max_length=255, unique=True, help_text='Full domain name')),
                ('domain_status', models.PositiveIntegerField(default=1, choices=[(1, 'Active'), (2, 'Pending lapse'), (3, 'Pending transfer away'), (4, 'Lapsed (inactive)'), (5, 'Transfered away')])),
                ('domain_type', models.PositiveIntegerField(default=1, choices=[(1, 'Business'), (2, 'Business security'), (3, 'Technical')])),
                ('website_type', models.PositiveIntegerField(default=3, choices=[(1, 'None'), (2, 'Redirect'), (3, 'Direct')], help_text='Type of website which domain refers to.')),
                ('website_url', models.URLField(max_length=255, blank=True, null=True, help_text='Website url which website type refers to.')),
            ],
            options={
                'abstract': False,
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, 'assets.baseobject', models.Model),
        ),
        migrations.CreateModel(
            name='DomainCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=255, unique=True)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='DomainContract',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
                ('expiration_date', models.DateField(blank=True, null=True)),
                ('price', models.DecimalField(verbose_name='Price', blank=True, null=True, help_text='Price for domain renewal for given period', max_digits=15, decimal_places=2)),
                ('domain', models.ForeignKey(to='domains.Domain')),
            ],
            options={
                'abstract': False,
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='DomainProviderAdditionalServices',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=255, unique=True)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='DomainRegistrant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=255, unique=True)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.AddField(
            model_name='domaincontract',
            name='registrant',
            field=models.ForeignKey(blank=True, null=True, to='domains.DomainRegistrant'),
        ),
        migrations.AddField(
            model_name='domain',
            name='additional_services',
            field=models.ManyToManyField(blank=True, to='domains.DomainProviderAdditionalServices'),
        ),
        migrations.AddField(
            model_name='domain',
            name='business_owner',
            field=models.ForeignKey(blank=True, null=True, help_text='Business contact person for a domain', related_name='domaincontract_business_owner', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='domain',
            name='business_segment',
            field=models.ForeignKey(blank=True, null=True, help_text='Business segment for a domain', to='assets.BusinessSegment'),
        ),
        migrations.AddField(
            model_name='domain',
            name='dns_provider',
            field=models.ForeignKey(blank=True, null=True, help_text="Provider which keeps domain's DNS", to='domains.DNSProvider'),
        ),
        migrations.AddField(
            model_name='domain',
            name='domain_category',
            field=models.ForeignKey(blank=True, null=True, to='domains.DomainCategory'),
        ),
        migrations.AddField(
            model_name='domain',
            name='domain_holder',
            field=models.ForeignKey(blank=True, null=True, help_text='Company which receives invoice for the domain', to='assets.AssetHolder'),
        ),
        migrations.AddField(
            model_name='domain',
            name='technical_owner',
            field=models.ForeignKey(blank=True, null=True, help_text='Technical contact person for a domain', related_name='domaincontract_technical_owner', to=settings.AUTH_USER_MODEL),
        ),
    ]
