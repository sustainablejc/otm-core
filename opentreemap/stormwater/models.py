# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.contrib.gis.db import models

from treemap.models import MapFeature


class PolygonalMapFeature(MapFeature):
    area_field_name = 'polygon'
    skip_detail_form = True

    polygon = models.MultiPolygonField(srid=3857)


class Bioswale(PolygonalMapFeature):
    pass
