# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import ralph.trade_marks.models
import ralph.lib.mixins.models


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('domains', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProviderAdditionalMarking',
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
            name='TradeMark',
            fields=[
                ('baseobject_ptr', models.OneToOneField(primary_key=True, serialize=False, auto_created=True, parent_link=True, to='assets.BaseObject')),
                ('name', models.CharField(verbose_name='Trade Mark name', max_length=255)),
                ('registrant_number', models.CharField(verbose_name='Registrant number', max_length=255)),
                ('type', models.PositiveIntegerField(verbose_name='Trade Mark type', default=2, choices=[(1, 'Word'), (2, 'Figurative'), (3, 'Word - Figurative')])),
                ('image', models.ImageField(blank=True, null=True, upload_to=ralph.trade_marks.models.upload_dir)),
                ('registrant_class', models.CharField(verbose_name='Registrant class', max_length=255)),
                ('valid_from', models.DateField(blank=True, null=True)),
                ('valid_to', models.DateField(blank=True, null=True)),
                ('order_number_url', models.URLField(max_length=255, blank=True, null=True)),
                ('status', models.PositiveIntegerField(verbose_name='Trade Mark status', default=5, choices=[(1, 'Application filed'), (2, 'Application refused'), (3, 'Application withdrawn'), (4, 'Application opposed'), (5, 'Registered'), (6, 'Registration invalidated'), (7, 'Registration expired')])),
                ('additional_markings', models.ManyToManyField(blank=True, to='trade_marks.ProviderAdditionalMarking')),
                ('business_owner', models.ForeignKey(related_name='trademark_business_owner', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, 'assets.baseobject'),
        ),
        migrations.CreateModel(
            name='TradeMarkAdditionalCountry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
            ],
            options={
                'verbose_name': 'Trade Mark Additional Country',
                'verbose_name_plural': 'Trade Mark Additional Countries',
            },
        ),
        migrations.CreateModel(
            name='TradeMarkCountry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('country', models.PositiveIntegerField(verbose_name='trade mark country', blank=True, null=True, default=153, choices=[(1, 'Afghanistan'), (2, 'Albania'), (3, 'Algeria'), (4, 'American Samoa'), (5, 'Andorra'), (6, 'Angola'), (7, 'Anguilla'), (8, 'Antarctica'), (9, 'Antigua and Barbuda'), (10, 'Argentina'), (11, 'Armenia'), (12, 'Aruba'), (13, 'Australia'), (14, 'Austria'), (15, 'Azerbaijan'), (16, 'Bahamas'), (17, 'Bahrain'), (18, 'Bangladesh'), (19, 'Barbados'), (20, 'Belarus'), (21, 'Belgium'), (22, 'Belize'), (23, 'Benin'), (24, 'Bermuda'), (25, 'Bhutan'), (26, 'Bolivia'), (27, 'Bosnia and Herzegovina'), (28, 'Botswana'), (29, 'Brazil'), (30, 'Brunei'), (31, 'Bulgaria'), (32, 'Burkina Faso'), (33, 'Burundi'), (34, 'Cambodia'), (35, 'Cameroon'), (36, 'Canada'), (37, 'Cape Verde'), (38, 'Cayman Islands'), (39, 'Central African Republic'), (40, 'Chad'), (41, 'Chile'), (42, 'China'), (43, 'Colombia'), (44, 'Comoros'), (45, 'Congo Brazzaville'), (46, 'Congo Kinshasa'), (47, 'Cook Islands'), (48, 'Costa Rica'), (49, 'Cote Divoire'), (50, 'Croatia'), (51, 'Cuba'), (52, 'Cyprus'), (53, 'Czech Republic'), (54, 'Denmark'), (55, 'Djibouti'), (56, 'Dominica'), (57, 'Dominican Republic'), (58, 'Ecuador'), (59, 'Egypt'), (60, 'El Salvador'), (61, 'Equatorial Guinea'), (62, 'Eritrea'), (63, 'Estonia'), (64, 'Ethiopia'), (65, 'Faroe Islands'), (66, 'Fiji'), (67, 'Finland'), (68, 'France'), (69, 'French Polynesia'), (70, 'Gabon'), (71, 'Gambia'), (72, 'Georgia'), (73, 'Germany'), (74, 'Ghana'), (75, 'Gibraltar'), (76, 'Greece'), (77, 'Grenada'), (78, 'Guam'), (79, 'Guatemala'), (80, 'Guinea Bissau'), (81, 'Guinea'), (82, 'Guyana'), (83, 'Haiti'), (84, 'Honduras'), (85, 'Hong Kong'), (86, 'Hungary'), (87, 'Iceland'), (88, 'India'), (89, 'Indonesia'), (90, 'Iran'), (91, 'Iraq'), (92, 'Ireland'), (93, 'Israel'), (94, 'Italy'), (95, 'Jamaica'), (96, 'Japan'), (97, 'Jersey'), (98, 'Jordan'), (99, 'Kazakhstan'), (100, 'Kenya'), (101, 'Kiribati'), (102, 'Kuwait'), (103, 'Kyrgyzstan'), (104, 'Laos'), (105, 'Latvia'), (106, 'Lebanon'), (107, 'Lesotho'), (108, 'Liberia'), (109, 'Libya'), (110, 'Liechtenstein'), (111, 'Lithuania'), (112, 'Luxembourg'), (113, 'Macau'), (114, 'Macedonia'), (115, 'Madagascar'), (116, 'Malawi'), (117, 'Malaysia'), (118, 'Maldives'), (119, 'Mali'), (120, 'Malta'), (121, 'Marshall Islands'), (122, 'Mauritania'), (123, 'Mauritius'), (124, 'Mexico'), (125, 'Micronesia'), (126, 'Moldova'), (127, 'Monaco'), (128, 'Mongolia'), (129, 'Montenegro'), (130, 'Montserrat'), (131, 'Morocco'), (132, 'Mozambique'), (133, 'Myanmar'), (134, 'Namibia'), (135, 'Nauru'), (136, 'Nepal'), (137, 'Netherlands Antilles'), (138, 'Netherlands'), (139, 'New Zealand'), (140, 'Nicaragua'), (141, 'Niger'), (142, 'Nigeria'), (143, 'North Korea'), (144, 'Norway'), (145, 'Oman'), (146, 'Pakistan'), (147, 'Palau'), (148, 'Panama'), (149, 'Papua New Guinea'), (150, 'Paraguay'), (151, 'Peru'), (152, 'Philippines'), (153, 'Poland'), (154, 'Portugal'), (155, 'Puerto Rico'), (156, 'Qatar'), (157, 'Romania'), (158, 'Russian Federation'), (159, 'Rwanda'), (160, 'Saint Lucia'), (161, 'Samoa'), (162, 'San Marino'), (163, 'Sao Tome and Principe'), (164, 'Saudi Arabia'), (165, 'Senegal'), (166, 'Serbia'), (167, 'Seychelles'), (168, 'Sierra Leone'), (169, 'Singapore'), (170, 'Slovakia'), (171, 'Slovenia'), (172, 'Solomon Islands'), (173, 'Somalia'), (174, 'South Africa'), (175, 'South Korea'), (176, 'Spain'), (177, 'Sri Lanka'), (178, 'St Kitts and Nevis'), (179, 'St Vincent and the Grenadines'), (180, 'Sudan'), (181, 'Suriname'), (182, 'Swaziland'), (183, 'Sweden'), (184, 'Switzerland'), (185, 'Syria'), (186, 'Tajikistan'), (187, 'Taiwan'), (188, 'Tanzania'), (189, 'Thailand'), (190, 'Timor Leste'), (191, 'Togo'), (192, 'Tonga'), (193, 'Trinidad and Tobago'), (194, 'Tunisia'), (195, 'Turkey'), (196, 'Turkmenistan'), (197, 'Turks and Caicos Islands'), (198, 'Tuvalu'), (199, 'Uganda'), (200, 'Ukraine'), (201, 'United Arab Emirates'), (202, 'United Kingdom'), (203, 'United States of America'), (204, 'Uruguay'), (205, 'Uzbekistan'), (206, 'Vanuatu'), (207, 'Vatican City'), (208, 'Venezuela'), (209, 'Viet Nam'), (210, 'Virgin Islands British'), (211, 'Virgin Islands US'), (212, 'Western Sahara'), (213, 'Yemen'), (214, 'Zambia'), (215, 'Zimbabwe'), (301, 'England'), (302, 'Northern Ireland'), (303, 'Wales'), (304, 'Scotland'), (601, 'Northern Cyprus'), (602, 'Palestine'), (603, 'Somaliland'), (901, 'African Union'), (902, 'Arab League'), (903, 'Association of Southeast Asian Nations'), (904, 'Caricom'), (905, 'Commonwealth of Independent States'), (906, 'Commonwealth of Nations'), (907, 'European Union'), (908, 'Islamic Conference'), (909, 'NATO'), (910, 'Olimpic Movement'), (911, 'OPEC'), (912, 'Red Cross'), (913, 'United Nations')])),
            ],
            bases=(ralph.lib.mixins.models.AdminAbsoluteUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='TradeMarkRegistrarInstitution',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=75)),
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
            name='TradeMarksLinkedDomains',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('domain', models.ForeignKey(related_name='trade_mark', to='domains.Domain')),
                ('trade_mark', models.ForeignKey(to='trade_marks.TradeMark')),
            ],
            options={
                'verbose_name': 'Trade Marks Linked Domain',
                'verbose_name_plural': 'Trade Marks Linked Domains',
            },
        ),
        migrations.AddField(
            model_name='trademarkadditionalcountry',
            name='country',
            field=models.ForeignKey(to='trade_marks.TradeMarkCountry'),
        ),
        migrations.AddField(
            model_name='trademarkadditionalcountry',
            name='trade_mark',
            field=models.ForeignKey(to='trade_marks.TradeMark'),
        ),
        migrations.AddField(
            model_name='trademark',
            name='domains',
            field=models.ManyToManyField(related_name='_trademark_domains_+', to='domains.Domain', through='trade_marks.TradeMarksLinkedDomains'),
        ),
        migrations.AddField(
            model_name='trademark',
            name='holder',
            field=models.ForeignKey(verbose_name='Trade Mark holder', blank=True, null=True, to='assets.AssetHolder'),
        ),
        migrations.AddField(
            model_name='trademark',
            name='registrar_institution',
            field=models.ForeignKey(null=True, to='trade_marks.TradeMarkRegistrarInstitution'),
        ),
        migrations.AddField(
            model_name='trademark',
            name='technical_owner',
            field=models.ForeignKey(related_name='trademark_technical_owner', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='trademarkslinkeddomains',
            unique_together=set([('trade_mark', 'domain')]),
        ),
        migrations.AlterUniqueTogether(
            name='trademarkadditionalcountry',
            unique_together=set([('country', 'trade_mark')]),
        ),
    ]
