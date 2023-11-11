import requests
from utilities import find_dict
from access_tokens import get_access_token


def get_deal_properties(deal_id_str):
    access_token_str = get_access_token('hubspot')
    url = f'https://api.hubapi.com/crm/v3/objects/deals/{deal_id_str}'
    headers = {
        'Authorization': f'Bearer {access_token_str}',
    }

    response = requests.get(url=url,
                            headers=headers)

    deal = response.json()
    return deal.get('properties', {})


def get_stage_name(stage_id_str):
    access_token_str = get_access_token('hubspot')
    url = 'https://api.hubapi.com/crm/v3/pipelines/deals'
    headers = {
        'Authorization': f'Bearer {access_token_str}',
    }

    response = requests.get(url=url,
                            headers=headers)
    stages = response.json().get('results', {})[0].get('stages')
    stage = find_dict(stages, 'id', stage_id_str)

    return stage['label']
