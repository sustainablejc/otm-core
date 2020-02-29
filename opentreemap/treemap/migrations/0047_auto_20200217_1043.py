# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2020-02-17 16:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('treemap', '0046_auto_20170907_0937'),
    ]

    operations = [
        migrations.CreateModel(
            name='MapFeaturePhotoLabel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('map_feature_photo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='treemap.MapFeaturePhoto')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='mapfeaturephotolabel',
            unique_together=set([('map_feature_photo', 'name')]),
        ),
    ]
