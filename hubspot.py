import requests
from translator import get_status_translator
from utilities import find_dict, get_key_from_value
from access_tokens import get_access_token
import json


class Deal:
    def __init__(self, deal_name = None, deal_id = None, deal_stage = None):
        self.deal_name = deal_name
        self.deal_id = deal_id
        self.deal_stage = deal_stage
        self.access_token = get_access_token(platform_str='hubspot')

        if not deal_id:
            self.deal_id = self.create_deal()

    def create_deal(self):
        # POST request to Hubspot API to create a new deal
        # The request might look something like this:
        url = f"https://api.hubapi.com/crm/v3/objects/deals/"
        headers = {"Authorization": f"Bearer {self.access_token}",
                   "Content-Type": "application/json"}
        data = {
            'properties': {
                'dealname': self.deal_name,
                'dealstage': self.deal_stage
            }
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))

        if response.status_code == 201:
            print("Deal created successfully!", f'Response: {response.text}')
        else:
            print(f"Failed to create Deal. Status code: {response.status_code}. Response: {response.text}")

        # Suppose the response is a JSON object and id is one of the fields
        return response.json().get('id', {})


    def update_deal_name(self, value):
        # POST request to Hubspot API to update a deal
        # The request might look something like this:
        url = f"https://api.hubapi.com/crm/v3/objects/deals/{self.deal_id}"
        headers = {"Authorization": f"Bearer {self.access_token}",
                   "Content-Type": "application/json"}
        data = {
            'properties': {
                'dealname': value,
            }
        }

        response = requests.patch(url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            print("Deal name updated successfully!", f'Response: {response.text}')
        else:
            print(f"Failed to update Deal. Status code: {response.status_code}. Response: {response.text}")

        # Suppose the response is a JSON object and id is one of the fields
        return response.json().get('id', {})


    def update_deal_stage(self, value):
        # POST request to Hubspot API to update a deal
        # The request might look something like this:
        url = f"https://api.hubapi.com/crm/v3/objects/deals/{self.deal_id}"
        headers = {"Authorization": f"Bearer {self.access_token}",
                   "Content-Type": "application/json"}
        data = {
            'properties': {
                'dealstage': value,
            }
        }

        response = requests.patch(url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            print("Deal stage updated successfully!", f'Response: {response.text}')
        else:
            print(f"Failed to update Deal. Status code: {response.status_code}. Response: {response.text}")

        # Suppose the response is a JSON object and id is one of the fields
        return response.json().get('id', {})


    def delete_deal(self):
        # POST request to Hubspot API to update a deal
        # The request might look something like this:
        url = f"https://api.hubapi.com/crm/v3/objects/deals/{self.deal_id}"
        headers = {"Authorization": f"Bearer {self.access_token}",
                   "Content-Type": "application/json"}

        response = requests.delete(url, headers=headers)

        if response.status_code == 200:
            print("Deal stage deleted successfully!", f'Response: {response.text}')
        else:
            print(f"Failed to delete Deal. Status code: {response.status_code}. Response: {response.text}")

        # Suppose the response is a JSON object and id is one of the fields
        return response.json().get('id', {})



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
