import requests
from flask import request
from translator import get_status_translator, get_objects_translator, update_objects_translator, \
    delete_object_record, get_folders_translator, update_folders_translator
from hubspot import get_deal_properties, Deal
from wrike import Project, get_project_id, get_project_name, get_project_info
from gdrive import copy_folder_to, move_file
from utilities import get_key_from_value
import time
from access_tokens import update_token, get_access_token
import json

def home():
    return "Hello, this is the home page!"


# install url https://app.hubspot.com/oauth/authorize?client_id=b2bcc660-28f7-4995-b224-0e0686f6fa96&redirect_uri=https:
# //mincka-servers.com/auth&scope=crm.objects.deals.read
# install url https://app.hubspot.com/oauth/authorize?client_id=b2bcc660-28f7-4995-b224-0e0686f6fa96&redirect_uri=https:
# //mincka-servers.com/auth&scope=crm.objects.deals.read%20crm.objects.deals.write

def handle_auth():
    code = request.args.get('code')
    # Use this authorization code to get an access token and refresh token
    data = {
        'grant_type': 'authorization_code',
        'client_id': 'b2bcc660-28f7-4995-b224-0e0686f6fa96',
        'client_secret': '94190740-1201-49a2-946b-9ca4e407704b',
        'redirect_uri': 'https://mincka-servers.com/auth',
        'code': code
    }

    response = requests.post('https://api.hubapi.com/oauth/v1/token', data=data)
    print(response.json())
    tokens = response.json()

    access_token = tokens.get('access_token')
    refresh_token = tokens.get('refresh_token')

    update_token('hubspot', access_token)
    update_token('hubspot_refresh', refresh_token)
    print("Received access token: ", access_token)
    print("Received refresh token: ", refresh_token)

    return "Authorization successful!", 200


def validate_hubspot_token(token):
    # The API endpoint you're using for the test request
    access_token = token
    url = f'https://api.hubapi.com/oauth/v1/access-tokens/{access_token}'
    headers = {
        'Content-Type': 'application/json',
    }
    response = requests.get(url, headers=headers)

    # Check the response to determine if the access token is valid
    if response.status_code == 200:
        # The access token is valid
        print("Access token is valid.")
    elif response.status_code == 404 or response.status_code == 401 or response.status_code == 400:
        # The access token is invalid or expired
        print("Access token is invalid or expired. Generating a new token")

        url = 'https://api.hubapi.com/oauth/v1/token'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Bearer {access_token}',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': '*/*'
        }
        # Replace with your actual refresh token and other required credentials
        refresh_token = get_access_token('hubspot_refresh')

        # Prepare the data payload for the refresh request
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': 'b2bcc660-28f7-4995-b224-0e0686f6fa96',
            'client_secret': '94190740-1201-49a2-946b-9ca4e407704b'
        }
        response = requests.post(url=url, headers=headers, data=json.dumps(data))
        request_url = response.request.url
        request_headers = response.request.headers
        request_body = response.request.body

        print("Request URL:", request_url)
        print("Request headers:", json.dumps(dict(request_headers), indent=4))
        print("Request body:", request_body)
        if response.status_code == 200:
            tokens = response.json()

            access_token = tokens.get('access_token')
            refresh_token = tokens.get('refresh_token')

            update_token('hubspot', access_token)
            update_token('hubspot_refresh', refresh_token)
            print(f"Tokens updated. Response: {response.text}")
        else:
            print(f"Failed to obtain tokens. Status code: {response.status_code}. Response: {response.text}")
    else:
        # Handle other potential errors
        print(f"An error occurred: {response.status_code}")


def respond():
    try:
        print(time.time())
        validate_hubspot_token(get_access_token('hubspot'))
        # time.sleep((0.1+random.random())/20)
        # read the data from the POST method.
        data = request.json[0]
        print(data)
        subscription_type = data.get('subscriptionType')
        property_name = data.get('propertyName')
        deal_id = str(data.get("objectId"))
        # call and get the translator for objects
        status_translator = get_status_translator()
        objects_translator = get_objects_translator()
        folders_translator = get_folders_translator()

        if subscription_type == 'deal.propertyChange' and property_name == "dealstage":
            deal_properties = get_deal_properties(deal_id_str=deal_id)
            update = False
            deal_status = str(deal_properties.get('dealstage'))
            if deal_id in objects_translator.keys():
                project_id = objects_translator[deal_id]
                print('project_id assigned')
            else:
                deal_name = deal_properties.get('dealname')
                project_id = get_project_id(project_name_str=deal_name)
                if project_id is not None:
                    update = True
                else:
                    project_status = status_translator[deal_status]
                    # Create a project in Wrike with the same name as the deal

                    project = Project(project_name=deal_name,
                                      parent_id='IEAEINT7I5AVW2QH',
                                      status_id=project_status)
                    project_id = project.project_id
                    update_objects_translator(hubspot_id_str=deal_id,
                                              wrike_id_str=project_id)
                    print('New project created from prop change')

            if deal_status in status_translator.keys():
                project_status = status_translator[deal_status]
                if project_id is None:
                    print('Project id not defined')
                else:
                    try:
                        project = Project(project_id=project_id)
                        project.update_status(project_status)
                        if update:
                            update_objects_translator(hubspot_id_str=deal_id,
                                                      wrike_id_str=project.project_id)
                    except Exception as e:
                        print(f"An unexpected error occurred: {e}")

            if deal_status == '184967120' and objects_translator[
                deal_id] not in folders_translator:  # offer elaboration
                if deal_id in objects_translator.keys():
                    project_name = get_project_name(project.project_id)
                folder_id = copy_folder_to(source_folder_id='130V1Kn6cIso_jUIR6YQx8ussuWT1NK4q',
                                           source_drive_id='0AJLZXfZRbFjuUk9PVA',
                                           destination_folder_id='14_cfdRROq-jV8IDh0jfmIin8vNB0Y8I5',
                                           destination_drive_id='0AIYZe1bK2f__Uk9PVA',
                                           project_name=project_name)
                if folder_id is not None:
                    update_folders_translator(wrike_id_str=project.project_id,
                                              gdrive_id_str=folder_id)

            if deal_status == '194277368':  # offer submitted
                move_file(file_id=folders_translator[project.project_id],
                          to_id='14bpYs33tvmQJsXcKQBQAncUXl4NjBEjX')

            if deal_status == 'closedwon':  # closed won
                project.project_name = get_project_name(project.project_id)
                project.enable()
                print('Project turned from Q to J')

        elif subscription_type == 'deal.creation':
            if deal_id not in objects_translator.keys():
                deal_properties = get_deal_properties(deal_id_str=deal_id)
                deal_name = deal_properties.get('dealname')
                deal_status = deal_properties.get('dealstage')
                project_status = status_translator[deal_status]
                # Create a project in Wrike with the same name as the deal

                project = Project(project_name=deal_name,
                                  parent_id='IEAEINT7I5AVW2QH',
                                  # development IEAEINT7I5CCL7HU deployment IEAEINT7I5AVW2QH
                                  status_id=project_status)
                update_objects_translator(hubspot_id_str=deal_id,
                                          wrike_id_str=project.project_id)
                print('New project created')
            else:
                print('project already exist')

        elif subscription_type == 'deal.deletion':

            if deal_id in objects_translator.keys():
                project_id = objects_translator[deal_id]
            else:
                project_id = None

            if project_id is None:
                print('Project id not defined')
            else:
                try:
                    project = Project(project_id=project_id)
                    project.delete()
                    delete_object_record(deal_id)

                except Exception as e:
                    print(f"An unexpected error occurred: {e}")

        if subscription_type == 'deal.propertyChange' and property_name == "dealname":

            new_name = str(data.get("propertyValue"))
            if deal_id in objects_translator.keys():
                project_id = objects_translator[deal_id]
                try:
                    project = Project(project_id=project_id)
                    project.change_name(new_name)
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
            else:
                deal_properties = get_deal_properties(deal_id_str=deal_id)
                deal_name = deal_properties.get('dealname')
                deal_status = deal_properties.get('dealstage')
                project_status = status_translator[deal_status]
                # Create a project in Wrike with the same name as the deal

                project = Project(project_name=deal_name,
                                  parent_id='IEAEINT7I5AVW2QH',
                                  # development IEAEINT7I5CCL7HU deployment IEAEINT7I5AVW2QH
                                  status_id=project_status)
                update_objects_translator(hubspot_id_str=deal_id,
                                          wrike_id_str=project.project_id)
                print('New project created')
                print('deal not in translator')

    except Exception as e:
        print(f"An unexpected error occurred in the handler: {e}")
    return {'status': 'success'}


# Define your event handling functions here for the wrike listener

def handle_folder_created(data):  # apply for projects
    project_id = data.get('folderId')
    project_info = get_project_info(project_id)
    project_name = project_info.get('title')
    project_status = project_info.get('project').get('customStatusId')
    deal_status = get_key_from_value(get_status_translator(), project_status)
    new_deal = Deal(deal_name=project_name, deal_stage=deal_status)
    update_objects_translator(hubspot_id_str=new_deal.deal_id, wrike_id_str=project_id)


def handle_folder_deleted(data):
    # Process event type B
    pass


def handle_folder_title_changed(data):
    project_name = data.get('title')
    project_id = data.get('folderId')
    deal_id = get_key_from_value(get_objects_translator(), project_id)
    deal = Deal(deal_id=deal_id)
    deal.update_deal_name(project_name)


def handle_folder_comment_added(data):
    # Process event type D
    pass


def handle_custom_field_changed(data):
    # Process event type E
    pass


def handle_project_status_changed(data):
    project_status = data.get('customStatusId')
    project_id = data.get('taskId')
    deal_id = get_key_from_value(get_objects_translator(), project_id)
    deal = Deal(deal_id=deal_id)
    deal_status = get_key_from_value(get_status_translator(), project_status)
    if deal_status is None:
        print('Status not in sales pipeline.')
    else:
        deal.update_deal_stage(deal_status)


# This dictionary maps event types to their corresponding functions

event_handlers = {
    'FolderCreated': handle_folder_created,
    'FolderDeleted': handle_folder_deleted,
    'FolderTitleChanged': handle_folder_title_changed,
    'FolderCommentAdded': handle_folder_comment_added,
    'FolderCustomFieldChanged': handle_custom_field_changed,
    'ProjectStatusChanged': handle_project_status_changed,
}


def respond_wrike():
    try:
        validate_hubspot_token(get_access_token('hubspot'))
        print('Token validated.')
        print(time.time())

        # read the data from the POST method.
        data = request.json[0]

        print(data)

        # Parse the JSON data from the request
        event_type = data.get('eventType')

        # Find the appropriate handler for the event type
        handler = event_handlers.get(event_type)

        # If a handler exists, call it with the event data
        if handler:
            handler(data)
            return 'Event handled', 200
        else:
            return 'No handler for event type', 400



    except Exception as e:
        print(f"An unexpected error occurred in the wrike handler: {e}")
    return {'status': 'success'}
