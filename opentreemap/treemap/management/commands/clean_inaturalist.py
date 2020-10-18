# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import logging
import requests

from django.core.management.base import BaseCommand
from django.db import transaction

from opentreemap.integrations import inaturalist
from treemap.instance import Instance
from treemap.models import Plot, Tree, INaturalistObservation

logger = logging.getLogger('')



class Command(BaseCommand):
    """
    Create a new instance with a single editing role.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            'instance_name',
            help='Specify instance name'),
        parser.add_argument(
            '--clean_missing',
            action='store_true',
            dest='clean_missing',
            help='Clean missing identifications'),
        parser.add_argument(
            '--sync',
            action='store_true',
            dest='sync',
            help='Sync identifications'),

    #@transaction.atomic
    def handle(self, *args, **options):
        name = options['instance_name']
        clean_missing = options['clean_missing']
        sync = options['sync']

        if clean_missing:
            self.clean_missing(name)
        elif sync:
            self.sync(name)

    def clean_missing(self, instance_name):
        instance = Instance.objects.get(name=instance_name)

        observations = INaturalistObservation.objects.all()
        observation_ids = inaturalist.get_all_observation_ids()

        observations_to_delete = []
        for observation in observations:
            if observation.observation_id not in observation_ids:
                observations_to_delete.append(observation)

        self.delete_observations(observations_to_delete)

    def sync(self, instance_name):
        instance = Instance.objects.get(name=instance_name)
        inaturalist.sync_identifications()

    @transaction.atomic
    def delete_observations(self, observations):
        for observation in observations:
            observation.delete()
        return True
