import dateutil.parser
import datetime
import time
import logging

from collections import Counter
from celery import shared_task, chord
import requests
from django.conf import settings
from django.db import connection
from django.core.cache import cache

from treemap.models import INaturalistObservation, Species, MapFeaturePhotoLabel, INaturalistPhoto
from treemap.lib.map_feature import get_map_feature_or_404

base_url = settings.INATURALIST_URL
api_url = settings.INATURALIST_API_URL


def get_inaturalist_auth_token():

    payload = {
        'client_id': settings.INATURALIST_APP_ID,
        'client_secret': settings.INATURALIST_APP_SECRET,
        'grant_type': 'password',
        'username': settings.INATURALIST_USERNAME,
        'password': settings.INATURALIST_PASSWORD
    }

    r = requests.post(
        url="{base_url}/oauth/token".format(base_url=base_url),
        data=payload
    )
    token = r.json()['access_token']
    return token


def get_inaturalist_jwt(token=None):
    if not token:
        token = get_inaturalist_auth_token()

    headers = {'Authorization': 'Bearer {}'.format(token)}

    response = requests.get(
        url="{base_url}/users/api_token".format(base_url=base_url),
        headers=headers
    )

    if not response.ok:
        raise Exception('Could not authenticate to get a JWT')

    return response.json()['api_token']


def set_observation_to_captive(token, observation_id):
    metric = 'wild'

    headers = {'Authorization': 'Bearer {}'.format(token)}
    params = {
        'id': observation_id,
        'metric': metric,
        'agree': 'false'
    }

    response = requests.post(
        url="{base_url}/observations/{observation_id}/quality/{metric}".format(
            base_url=base_url,
            observation_id=observation_id,
            metric=metric),
        json=params,
        headers=headers
    )

    return response.ok


def create_observation(token, latitude, longitude, species):

    headers = {'Authorization': 'Bearer {}'.format(token)}
    params = {'observation': {
        'observed_on_string': datetime.datetime.now().isoformat(),
        'latitude': latitude,
        'longitude': longitude,
        'species_guess': species
    }
    }

    response = requests.post(
        url="{base_url}/observations.json".format(base_url=base_url),
        json=params,
        headers=headers
    )

    observation = response.json()[0]

    set_observation_to_captive(token, observation['id'])

    return observation


def add_photo_to_observation(token, observation_id, photo):

    headers = {'Authorization': 'Bearer {}'.format(token)}
    data = {'observation_photo[observation_id]': observation_id}
    file_data = {'file': photo.image.file.file}

    response = requests.post(
        url="{base_url}/observation_photos".format(base_url=base_url),
        headers=headers,
        data=data,
        files=file_data
    )
    return response.json()


def match_species(common_name, species_name, species_map):
    """
    Rules to match iNaturalist species to OTM species names
    """
    common_name = common_name.lower()
    common_name_map = {
        'london plane': 'london planetree'
    }
    common_name = common_name_map.get(common_name, common_name)

    species = species_map.get(common_name)

    if species is None:
        _species_name = species_name.lower()
        species_by_species_name = [s for s in species_map.values()
            if _species_name == '{} {}'.format(s.genus, s.species).lower()]
        if len(species_by_species_name) == 1:
            species = species_by_species_name[0]
    return species


def sync_identifications():
    """
    Goes through all unidentified observations and updates them with taxonomy on iNaturalist
    """
    logger = logging.getLogger('iNaturalist')
    # a map of common name to the actual species
    species_map = {s.common_name.lower(): s for s in Species.objects.all()}

    o9n_models = {o.observation_id: o for o in INaturalistObservation.objects.filter(is_identified=False)}
    observation_ids = get_all_observation_ids(identifications='most_agree', hrank='species')

    # these are the observations we can work with
    potential_observation_ids = set(observation_ids).intersection(
        set(o9n_models.keys()))

    found_identifications = []
    for observation_id in list(potential_observation_ids)[:100]:
        observation = get_observation_by_id(observation_id)
        if not observation:
            continue
        species_guess = observation['species_guess']
        identifications = observation['identifications']

        species_name_counter = Counter([i['taxon']['name'] for i in identifications])

        # if the top 2 have the same count, then we can't pick a mostly agree
        if (len(identifications) < 2
            # this is true if the top 2 counts have the same number
            or len(set([count for _, count in species_name_counter.most_common(2)])) != len(species_name_counter)):
            logger.info('More than one most common species for observation_id {}. Skipping'.format(observation_id))
            continue

        species_name, _ = species_name_counter.most_common(1)[0]
        try:
            common_name, _ = Counter([i['taxon']['preferred_common_name'] for i in identifications]).most_common()[0]
        except:
            import ipdb; ipdb.set_trace() # BREAKPOINT
            pass

        species = match_species(common_name, species_name, species_map)
        if not species:
            logger.error('Cannot find species {}; common name {}'.format(species_name, common_name))
            continue

        found_identifications.append((observation_id, species))
        time.sleep(1)


    import ipdb; ipdb.set_trace() # BREAKPOINT
    for o9n_model in o9n_models:
        taxonomy = observations.get(o9n_model.observation_id)
        if taxonomy:
            _set_identification(o9n_model, taxonomy)


def can_trust_user(user):
    """
    We can trust a user if we have the user in our list
    of trusted users or if the user has over 1k identifications
    """
    return True


def get_validated_species_info(inaturalist_observation):
    """
    Using the raw json from iNaturalist, we want to check if we can use this
    as a valid identification

    Some rules:
        - At least 3 identifications

    FIXME: What to do about num_identifications_disagreements?

    Returns None if the validation is no good
    """
    if inaturalist_observation.get('identifications_count', 0) < 3:
        return None

    inaturalist_identifications = inaturalist_observation['identifications']
    taxons = [
        #'user': i['user'],
        i['taxon'] for i in inaturalist_identifications
        if can_trust_user(i['user'])]

    # check that the majority agree
    taxon_counter = Counter([t['name'] for t in taxons])
    taxon_most_common = taxon_counter.most_common()

    # if we have multiple, and the most common one has the same
    # count as the second most common one, then we do not have a majority
    if len(taxon_counter) > 1 and taxon_most_common[0][1] == taxon_most_common[1][1]:
        return None

    taxon = [t for t in taxons
            if t['name'] == taxon_most_common[0][0]][0]
    genus, species = taxon.split(' ')
    return {
        'genus': genus,
        'species': species,
        'common_name': taxon['preferred_common_name']
    }


def get_all_observation_ids(**kwargs):
    jwt = get_inaturalist_jwt()

    headers = {'Authentication': jwt}
    ids = []
    page = 1
    while(True):
        arguments = {
            "user_login": settings.INATURALIST_USERNAME,
            "only_id": "true",
            "per_page": "200",
            "page": "{page}".format(page=page)
        }
        if kwargs:
            arguments.update(kwargs)

        args = "&".join(["{}={}".format(key, value) for key, value in arguments.items()])

        url = "{base_url}/observations?{args}".format(base_url=api_url, args=args)
        response = requests.get(
            url=url,
            headers=headers
        )

        results = response.json()['results']
        if not results:
            break

        ids.extend([result['id'] for result in results])
        page += 1

    return ids


def get_all_observations():
    """
    Retrieve iNaturalist observation by ID
    API docs: https://www.inaturalist.org/pages/api+reference#get-observations-id

    We want to retrieve all observations that have at least two observations in agreement

    :param o9n_id: observation ID
    :return: observation JSON as a dict
    """
    all_data = []
    page = 1
    per_page = 100
    while(True):
        data = requests.get(
            url="{base_url}/observations.json".format( base_url=base_url),
            params={
                'user_id': 'sustainablejc',
                'identifications': 'most_agree',
                'per_page': per_page,
                'page': page
            }
        ).json()
        if (not data):
            break

        all_data.extend(data)

        page += 1
        time.sleep(10)

    return {d['id']: {'updated_at': d['updated_at'], 'taxon': d['taxon']} for d in all_data}


def get_o9n(o9n_id):
    """
    Retrieve iNaturalist observation by ID
    API docs: https://www.inaturalist.org/pages/api+reference#get-observations-id
    :param o9n_id: observation ID
    :return: observation JSON as a dict
    """
    return requests.get(
        url="{base_url}/observations/{o9n_id}.json".format(
            base_url=base_url, o9n_id=o9n_id)
    ).json()


def _set_identification(o9n_model, species):
    o9n_model.tree.species = Species(common_name=taxon['taxon']['common_name']['name'])
    o9n_model.identified_at = dateutil.parser.parse(taxon['updated_at'])
    o9n_model.is_identified = True
    o9n_model.save()


def get_features_for_inaturalist(tree_id=None):
    """
    Get all the features that have a label and can be submitted to iNaturalist
    """
    tree_filter_clause = "1=1"
    if tree_id:
        tree_filter_clause = "t.id = {}".format(tree_id)

    query = """
        SELECT  photo.map_feature_id, photo.instance_id
        FROM    treemap_mapfeaturephoto photo
        JOIN    treemap_mapfeaturephotolabel label on label.map_feature_photo_id = photo.id
        JOIN    treemap_tree t on t.plot_id = photo.map_feature_id
        LEFT JOIN treemap_inaturalistobservation inat on inat.map_feature_id = photo.map_feature_id
        where   1=1
        and     inat.id is null

         -- these could be empty tree pits
        and     t.species_id is not null

        -- we also cannot get the species to dead trees
        and     coalesce(t.udfs -> 'Condition', '') != 'Dead'

        -- if we should filter a specific tree, do it here
        and     {}

        group by photo.map_feature_id, photo.instance_id
        having sum(case when label.name = 'shape' then 1 else 0 end) > 0
        and sum(case when label.name = 'bark'  then 1 else 0 end) > 0
        and sum(case when label.name = 'leaf'  then 1 else 0 end) > 0
    """.format(tree_filter_clause)

    with connection.cursor() as cursor:
        # FIXME use parameters for a tree id
        cursor.execute(query)
        results = cursor.fetchall()

    return [{'feature_id': r[0],
             'instance_id': r[1]}
            for r in results]


@shared_task()
def create_observations(instance, tree_id=None):
    logger = logging.getLogger('iNaturalist')
    logger.info('Creating observations')

    features = get_features_for_inaturalist(tree_id)
    if not features:
        return

    token = get_inaturalist_auth_token()

    for feature in features:
        feature = get_map_feature_or_404(feature['feature_id'], instance)
        tree = feature.safe_get_current_tree()

        if not tree:
            continue

        photos = tree.photos().prefetch_related('mapfeaturephotolabel_set').all()
        if len(photos) != 3:
            continue

        # we want to submit the leaf first, so sort by leaf
        photos = sorted(photos, key=lambda x: 0 if x.has_label('leaf') else 1)
        (longitude, latitude) = feature.latlon.coords

        # create the observation
        _observation = create_observation(
            token,
            latitude,
            longitude,
            tree.species.common_name
        )
        observation = INaturalistObservation(
            observation_id=_observation['id'],
            map_feature=feature,
            tree=tree,
            submitted_at=datetime.datetime.now()
        )
        observation.save()

        for photo in photos:
            time.sleep(10)
            photo_info = add_photo_to_observation(token, _observation['id'], photo)

            photo_observation = INaturalistPhoto(
                tree_photo=photo,
                observation=observation,
                inaturalist_photo_id=photo_info['photo_id']
            )
            photo_observation.save()

        # let's not get rate limited
        time.sleep(30)

    logger.info('Finished creating observations')
