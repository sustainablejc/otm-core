# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2020-05-08 01:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('treemap', '0049_auto_20200229_2200'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdefinedfielddefinition',
            name='isrequired',
            field=models.BooleanField(default=False),
        ),
    ]
