# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import json
import logging
import requests
import time

from django.core.management.base import BaseCommand
from django.db import transaction

from opentreemap.integrations import inaturalist
from treemap.instance import Instance
from treemap.models import Species, Plot, Tree, INaturalistObservation, INaturalistSpecies

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
        parser.add_argument(
            '--species_to_json',
            action='store_true',
            dest='species_to_json',
            help=''),
        parser.add_argument(
            '--fill_species',
            action='store_true',
            dest='fill_species',
            help=''),
        parser.add_argument(
            '--filename',
            action='store',
            dest='filename',
            help='Filename'),
        parser.add_argument(
            '--genus_to_json',
            action='store_true',
            dest='genus_to_json',
            help=''),

    #@transaction.atomic
    def handle(self, *args, **options):
        name = options['instance_name']
        clean_missing = options['clean_missing']
        sync = options['sync']
        fill_species = options['fill_species']
        species_to_json = options['species_to_json']
        #fill_genus = options['fill_genus']
        genus_to_json = options['genus_to_json']
        filename = options['filename']

        if clean_missing:
            self.clean_missing(name)
        elif sync:
            self.sync(name)
        elif species_to_json:
            self.species_to_json(filename)
        elif fill_species:
            self.fill_species(filename)
        elif genus_to_json:
            self.genus_to_json(filename)

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

    def species_to_json(self, filename):
        species_list = []
        species = Species.objects.all()
        for s in species:
            inaturalist_species = inaturalist.get_species(s)
            species_list.append((s, inaturalist_species))
            if inaturalist_species is not None:
                time.sleep(10)

        with open(filename, 'w') as fd:
            json.dumps([{
                    'otm': model_to_dict(s[0]),
                    'inaturalist': model_to_dict(s[1]) if s[1] else None
                } for s in species_list], fd)

    def fill_species(self, filename):
        with open(filename, 'r') as fd:
            data = json.load(fd)

        inaturalist_species_list = []
        for datum in data:
            inaturalist = datum['inaturalist']
            if inaturalist is None or inaturalist['preferred_common_name'] is None:
                continue
            species = Species.objects.get(pk=datum['otm']['id'])
            inaturalist_species = INaturalistSpecies(
                inaturalist_id = inaturalist['inaturalist_id'],
                preferred_common_name = inaturalist['preferred_common_name'],
                genus = inaturalist['genus'],
                species_name = inaturalist.get('species_name'),
                name = inaturalist['name'],
                species = species
            )
            inaturalist_species_list.append(inaturalist_species)

        INaturalistSpecies.objects.bulk_create(inaturalist_species_list)

    def genus_to_json(self, filename):
        species_list = []
        species = Species.objects.filter(species='').all()
        for s in species:
            inaturalist_species = inaturalist.get_species(s, rank='genus')
            species_list.append((s, inaturalist_species))
            if inaturalist_species is not None:
                time.sleep(10)

        with open(filename, 'w') as fd:
            json.dumps([{
                    'otm': model_to_dict(s[0]),
                    'inaturalist': model_to_dict(s[1]) if s[1] else None
                } for s in species_list], fd)
