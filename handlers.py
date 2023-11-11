import requests
from flask import Flask, request
from translator import get_status_translator, get_objects_translator, update_objects_translator, \
    update_status_translator, delete_object_record
from access_tokens import get_access_token
from hubspot import get_deal_properties
from wrike import Project, get_project_id


def home():
    return "Hello, this is the home page!"

#install url https://app.hubspot.com/oauth/authorize?client_id=b2bcc660-28f7-4995-b224-0e0686f6fa96&redirect_uri=https://mincka-servers.com/auth&scope=crm.objects.deals.read
def handle_auth():
    code = request.args.get('code')
    # Use this authorization code to get an access token and refresh token
    data = {
        'grant_type': 'authorization_code',
        'client_id': 'b2bcc660-28f7-4995-b224-0e0686f6fa96',
        'client_secret': '94190740-1201-49a2-946b-9ca4e407704b',
        'redirect_uri': 'mincka-servers.com/auth',
        'code': code
    }

    response = requests.post('https://api.hubapi.com/oauth/v1/token', data=data)
    print(response.json())
    tokens = response.json()

    access_token = tokens.get('access_token')
    refresh_token = tokens.get('refresh_token')

    print("Received access token: ", access_token)
    print("Received refresh token: ", refresh_token)

    return {"Authorization successful!", 200}


def respond():
    try:
        # read the data from the POST method.
        data = request.json[0]
        print(data)
        subscription_type = data.get('subscriptionType')
        deal_id = str(data.get("objectId"))
        # call and get the translator for objects
        status_translator = get_status_translator()
        objects_translator = get_objects_translator()

        if subscription_type == 'deal.propertyChange':
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

        elif subscription_type == 'deal.creation':
            deal_properties = get_deal_properties(deal_id_str=deal_id)
            deal_name = deal_properties.get('dealname')
            deal_status = deal_properties.get('dealstage')
            project_status = status_translator[deal_status]
            # Create a project in Wrike with the same name as the deal

            project = Project(project_name=deal_name,
                              parent_id='IEAEINT7I5AVW2QH', # development IEAEINT7I5CCL7HU deployment IEAEINT7I5AVW2QH
                              status_id=project_status)
            update_objects_translator(hubspot_id_str=deal_id,
                                      wrike_id_str=project.project_id)

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
    except Exception as e:
        print(f"An unexpected error occurred in the handler: {e}")
    return {'status': 'success'}
    print('success')
