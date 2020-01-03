# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-07 14:37


from django.db import migrations
import treemap.DotDict
import treemap.json_field


class Migration(migrations.Migration):

    dependencies = [
        ('treemap', '0045_add_modeling_permission'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instance',
            name='config',
            field=treemap.json_field.JSONField(blank=True, default=treemap.DotDict.DotDict),
        ),
    ]
