import copy
import json

# API reference: https://www.inaturalist.org/pages/api+reference#get-observations-id
with open('opentreemap/integrations/tests/fixtures/observation.json') as json_file:
    _o9n = json.loads(json_file.read())

# API reference:
# curl -X GET --header 'Accept: application/json' curl -X GET --header 'Accept: application/json' 'https://api.inaturalist.org/v1/observations?rank=species&user_login=sustainablejc&identifications=most_agree&order=desc&order_by=created_at'
with open('opentreemap/integrations/tests/fixtures/inaturalist_observation_multiple_identifications.json') as json_file:
    inaturalist_observation_multiple_identifications = json.loads(json_file.read())

def get_inaturalist_observation(observation_id=None):
    with open('opentreemap/integrations/tests/fixtures/inaturalist_observation_multiple_identifications.json') as json_file:
        inaturalist_observation_multiple_identifications = json.loads(json_file.read())
    return inaturalist_observation_multiple_identifications


def get_inaturalist_o9n(o9n_id=None):
    o9n_copy = copy.deepcopy(_o9n)

    if o9n_id:
        o9n_copy['id'] = o9n_id

    return o9n_copy
