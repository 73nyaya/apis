import requests, time, json
import pandas as pd
from flask import request
from translator import get_status_translator, get_objects_translator, update_objects_translator, \
    delete_object_record, get_folders_translator, update_folders_translator, get_translator,  \
        update_translator, delete_translator_record, Translators
from hubspot import get_deal_properties, Deal
from wrike import Project, get_project_id, get_project_name, get_project_info
from gdrive import copy_folder_to, move_file, create_folder
from utilities import get_key_from_value, find_dict, find_dict_in_list
from access_tokens import update_token, get_access_token
from enum import Enum
from typing import Optional


class connection_info(Enum):
    client_id = 'b2bcc660-28f7-4995-b224-0e0686f6fa96'
    client_secret = '94190740-1201-49a2-946b-9ca4e407704b'
    redirect_uri = 'https://mincka-servers.com/auth'


def home():
    return "Hello, this is the home page!"


def handle_auth() -> str:
    code = request.args.get('code')
    # Use this authorization code to get an access token and refresh token
    data = {
        'grant_type': 'authorization_code',
        'client_id': connection_info.client_id.value,
        'client_secret': connection_info.client_secret.value,
        'redirect_uri': connection_info.redirect_uri.value,
        'code': code
    }

    response = requests.post('https://api.hubapi.com/oauth/v1/token', data=data)
    print(response.json())
    tokens = response.json()

    access_token = tokens.get('access_token')
    refresh_token = tokens.get('refresh_token')

    if response.status_code == 200:
        update_token('hubspot', access_token)
        update_token('hubspot_refresh', refresh_token)
        return f"Authorization successful! Response: {response.text}. Status code: {response.status_code}"
    else:
        return f"An error occurred. Response: {response.text}. Status code: {response.status_code}"
    


def validate_hubspot_token(token: str) -> None:
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
            'client_id': connection_info.client_id.value,
            'client_secret': connection_info.client_secret.value
        }
        response = requests.post(url=url, headers=headers, data=data)
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
        print(f"An error occurred: {response.status_code}. Response: {response.text}")


def respond() -> dict:
    try:
        print(time.time())
        validate_hubspot_token(get_access_token('hubspot'))
        # read the data from the POST method.
        data = request.json[0]
        print(data)
        subscription_type = data.get('subscriptionType')
        change_source = data.get('changeSource')
        property_name = data.get('propertyName')
        deal_id = str(data.get("objectId"))
        # call and get the translator for objects
        status_translator = get_status_translator()
        objects_translator = get_objects_translator()
        folders_translator = get_folders_translator()

        if subscription_type == 'deal.propertyChange' and property_name == "dealstage":
            deal_properties = get_deal_properties(deal_id=deal_id)
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
                deal_properties = get_deal_properties(deal_id=deal_id)
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

        if subscription_type == 'deal.propertyChange' and property_name == "dealname" and change_source != 'INTEGRATION':

            new_name = str(data.get("propertyValue"))
            if deal_id in objects_translator.keys():
                project_id = objects_translator[deal_id]
                try:
                    project = Project(project_id=project_id)
                    project.change_name(new_name)
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
            else:
                deal_properties = get_deal_properties(deal_id=deal_id)
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

def handle_folder_created(data) -> None:  # apply for projects
    project_id = data.get('folderId')
    if project_id not in get_translator(translator_case=Translators.objects.value).values():
        project_info = get_project_info(project_id)
        project_name = project_info.get('title')
        project_status = project_info.get('project').get('customStatusId')
        deal_status = get_key_from_value(get_status_translator(), project_status)
        if deal_status:
            new_deal = Deal(deal_name=project_name, deal_stage=deal_status)
            update_objects_translator(hubspot_id_str=new_deal.deal_id, wrike_id_str=project_id)
        else:
            print('project status not found in hubspot. Aborting deal creation.')
    else: 
        print('Deal already exist.')


def handle_folder_deleted(data: dict) -> None:
    project_id = data.get('folderId')
    deal_id = get_key_from_value(get_objects_translator(), project_id)
    if deal_id is None:
        print('Project not in translator')
    else:
        deal = Deal(deal_id=deal_id)
        deal.delete_deal()
        delete_object_record(deal_id)

def handle_folder_title_changed(data: dict) -> None:
    project_name = data.get('title')
    project_id = data.get('folderId')
    deal_id = get_key_from_value(get_objects_translator(), project_id)
    deal_old_name = get_deal_properties(deal_id).get('dealname')
    deal = Deal(deal_id=deal_id)
    if deal_old_name[1:] != project_name[1:]:
        deal.update_deal_name("Q" + project_name[1:])


def handle_folder_comment_added(data):
    # Process event type D
    pass


def handle_custom_field_changed(data):
    # Process event type E
    pass


def handle_project_status_changed(data: dict) -> None:
    project_status = data.get('customStatusId')
    project_id = data.get('taskId')
    if project_status == 'IEAEINT7JMCLXBAC':
        print('Creating project folder')
        try:
            create_project_folder(project_id=project_id)
        except Exception as e:
            print('Failed to create project, unexpected error: ', e)
    deal_id = get_key_from_value(get_objects_translator(), project_id)
    if deal_id:
        deal = Deal(deal_id=deal_id)
        deal_status = get_key_from_value(get_status_translator(), project_status)
        deal_old_status = get_deal_properties(deal_id)
        if deal_status != deal_old_status:
            if deal_status is None:
                print('Status not in sales pipeline.')
            else:
                deal.update_deal_stage(deal_status)
        else:
            print('deal status has not changed')
    else:
        print('deal id not found.')



def create_project_folder(project_id: str) -> Optional[str]:
    project = Project(project_id=project_id)
    project_information = get_project_info(project_id_str=project_id)
    custom_fields = project_information.get('customFields')
    print(custom_fields)
    print('searching customer:')
    customer = find_dict_in_list(my_list=custom_fields, target_key='id', target_val='IEAEINT7JUACLO7Y')['value']
    if customer =="":
        project.write_comment('Customer was not been specified to create the google drive project folder. Please create it manually.')
    else: 
        print(f'Customer: {customer}')
    print('searching folder structure:')
    folder_structure = find_dict_in_list(my_list=custom_fields, target_key='id', target_val='IEAEINT7JUAFPH5S')['value']
    if folder_structure=="":
        project.write_comment('Folder structure custom field was not been specified to create the google drive project folder. Please create it manually.')
    else: 
        print(f'Folder structure: {folder_structure}')
    folder_types_translator = get_translator(translator_case=Translators.folder_types.value) 
    project_folders_translator = get_translator(translator_case=Translators.project_folders.value)
    if project_id in project_folders_translator.keys():
        project.write_comment(f'Project folder already created. Please go to: https://drive.google.com/drive/u/0/folders/{project_folders_translator[project_id]}')
    else:
        if folder_structure in folder_types_translator.keys():
            source_folder_id = folder_types_translator[folder_structure]
        else:
            print(f'Creating new template structure for {folder_structure} project types')
            parent_id = '1_96_4Z7nCQXslAjV2E06psewBg1gKWKo' # Project directories organisation / project types
            source_folder_id = create_folder(parent_id=parent_id, folder_name=folder_structure)
            update_translator(translator_case=Translators.folder_types.value, key=folder_structure, value=source_folder_id)
            project.write_comment(f'The folder structure has not been defined for the project type: {folder_structure}. Please create it in the Engineering Templates/Project directories organisation/Project types folder in order to replicate for future cases.')
        destination_folder_id = validate_customer_folder(customer=customer)
        if destination_folder_id and source_folder_id:
            folder_id = copy_folder_to(source_folder_id=source_folder_id,
                                    source_drive_id='0AJLZXfZRbFjuUk9PVA', # Business operations shared drive 
                                    destination_folder_id= destination_folder_id, #projects 2024 drive folder
                                    destination_drive_id='0AO68U2ZGqB9JUk9PVA', # Engineering shared drive
                                    project_name=project_information.get('title'))
            update_translator(translator_case=Translators.project_folders.value, key=project_id, value = folder_id)
            project.write_comment(f'Project folder has been created. Please go to: https://drive.google.com/drive/u/0/folders/{folder_id}')
            return folder_id
        else: 
            print('An unexpected error occured when creating the project folder')
            project.write_comment('An unexpected error occurred when creating the projec folder in Google Drive, please verify and create it manually.')



def validate_customer_folder(customer:str) -> str:
    '''validates the existence of the customer folder in google drive'''
    parent_id='1ha3TKy3pRTEVv0tEAx6moS0ixir8Ydfx' #projects 2024 drive folder
    customer_folders_translator = get_translator(translator_case=Translators.customer_folders.value)
    if customer in customer_folders_translator.keys():
        print('customer folder already exist.')
        folder_id = customer_folders_translator[customer]
        return folder_id
    else:
        print('customer folder does not exist, creating a new one.')
        folder_id = create_folder(parent_id=parent_id, folder_name=customer)
        update_translator(translator_case=Translators.customer_folders.value, key=customer, value=folder_id)
        return folder_id


# This dictionary maps event types to their corresponding functions

event_handlers = {
    'FolderCreated': handle_folder_created,
    'FolderDeleted': handle_folder_deleted,
    'FolderTitleChanged': handle_folder_title_changed,
    'FolderCommentAdded': handle_folder_comment_added,
    'FolderCustomFieldChanged': handle_custom_field_changed,
    'ProjectStatusChanged': handle_project_status_changed,
}


def respond_wrike() -> dict:
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


def redirect_asset(asset_id) -> str:
    try:
        df = pd.read_excel('./Components/Data/redirects.xlsx')  # Assuming your file is named 'assets.xlsx'
        # Convert the DataFrame to a dictionary with asset_id as the key and custom_url as the value
        asset_redirects = dict(zip(df['asset_id'], df['drive_url']))
        new_url = asset_redirects.get(asset_id)
        return new_url
    except Exception as e:
        print("an error ocurred redirecting:", e)
        return None

