import requests
import json
from utilities import find_dict
from access_tokens import get_access_token
from typing import Dict, Optional

# status_id = "IEAEINT7JMDWY7CM"
# {
#            "id": "IEAEINT7I5CCL7HU",
#            "title": "8. Testing & Development",
#            "avatarUrl": "https://www.wrike.com/static/spaceicons2/v3/9/9-explore-2.png",
#            "accessType": "Private",
#            "archived": false,
#            "defaultProjectWorkflowId": "IEAEINT7K773XSMB",
#            "defaultTaskWorkflowId": "IEAEINT7K773XSMB"
#        }

class Project:

    def __init__(self, project_name: Optional[str]=None, status_id: Optional[str]=None, project_id: Optional[str]=None, parent_id: Optional[str]=None):
        self.project_id = project_id
        self.access_token = get_access_token(platform_str='wrike')
        self.project_name = project_name
        self.status_id = status_id
        self.parent_id = parent_id

        # If project_id isn't provided, a new project will be created
        if not project_id:
            self.project_id = self.create_project()

    def create_project(self) -> str:
        # POST request to Wrike API to create a new project
        # The request might look something like this:
        url = f"https://www.wrike.com/api/v4/folders/{self.parent_id}/folders/"
        headers = {"Authorization": f"Bearer {self.access_token}",
                   "Content-Type": "application/json"}
        data = {
            "title": self.project_name,
            "project": {
                "customStatusId": self.status_id
            }
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            print("Project created successfully!", f'Response: {response.text}')
        else:
            print(f"Failed to create project. Status code: {response.status_code}. Response: {response.text}")

        # Suppose the response is a JSON object and id is one of the fields
        return response.json().get('data', {})[0].get('id')

    def get_status_id(self) -> str:
        # Here, you would usually make a GET request to Wrike API to fetch the current status.
        # The request might look something like this:
        if self.status_id:
            return self.status_id
        else:
            url = f"https://www.wrike.com/api/v4/folders/{self.project_id}"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"}
            response = requests.get(url, headers=headers)

            # Suppose the response is a JSON object and status is one of the fields
            self.status_id = response.json().get('data', {}).get('project', {}).get('customStatusId')
            print(self.status_id)
            return self.status_id 

    def update_status(self, target_status_str: str) -> None:
        old_status = self.get_status_id
        if old_status != target_status_str:
            url = f"https://www.wrike.com/api/v4/folders/{self.project_id}"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"}

            data = {
                "project": {
                    "customStatusId": target_status_str
                }
            }

            
            response = requests.put(url=url, headers=headers, data=json.dumps(data))

            if response.status_code == 200:
                print("Project status updated successfully!")
            else:
                print(f"Failed to update project status. Status code: {response.status_code}. Response: {response.text}")

            self.status_id = response.json().get('data', {})[0].get('project', {}).get('customStatusId')

    def change_name(self, new_name: str) -> None:
        url = f"https://www.wrike.com/api/v4/folders/{self.project_id}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"}

        data = {
            "title": str(new_name)
        }
        response = requests.put(url=url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            print("Project name updated successfully!", f'Response: {response.text}')
        else:
            print(f"Failed to update project name. Status code: {response.status_code}. Response: {response.text}")

        self.project_name = response.json().get('data', {})[0].get('title', {})

    def enable(self) -> None:
        try:
            self.change_name("J" + self.project_name[1:])
            self.move_project('IEAEINT7I4UAB54L')
            self.write_comment(
                'Hi <a class="stream-user-id avatar" rel="KX72MPGT">@Developers</a>! This offer has been accepted. '
                'Please, start scheduling the work.')
            self.create_adm_folder()
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def delete(self) -> None:
        url = f"https://www.wrike.com/api/v4/folders/{self.project_id}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"}
        response = requests.delete(url=url, headers=headers)
        if response.status_code == 200:
            print("Project deleted successfully!", f'Response: {response.text}')
        else:
            print(f"Failed to delete project. Status code: {response.status_code}. Response: {response.text}")

    def move_project(self, destination_folder_id: str) -> None:
        url = f"https://www.wrike.com/api/v4/folders/{self.project_id}?"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"}

        data = {
            'addParents': [str(destination_folder_id)],
            'removeParents': ['IEAEINT7I5AVW2QH'],
            "project": {
                "ownersAdd": ['KUAJV4AW']  # Leo B
            }
        }
        response = requests.put(url=url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            print("Project moved successfully!")
        else:
            print(f"Failed to move project. Status code: {response.status_code}. Response: {response.text}")

    def write_comment(self, message_str: str) -> None:
        url = f"https://www.wrike.com/api/v4/folders/{self.project_id}/comments"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"}

        data = {
            "text": message_str
        }
        response = requests.post(url=url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            print("comment successfully!")
        else:
            print(f"Failed to comment. Status code: {response.status_code}. Response: {response.text}")

    def create_adm_folder(self) -> None:
        # POST request to Wrike API to create a new project
        # The request might look something like this:
        url = f"https://www.wrike.com/api/v4/folders/{self.project_id}/folders/"
        headers = {"Authorization": f"Bearer {self.access_token}",
                   "Content-Type": "application/json"}
        data = {
            "title": self.project_name[:7] + "(ADM) " + self.project_name[7:],
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            print("ADM folder created successfully!", f'Response: {response.text}')
        else:
            print(f"Failed to create ADM folder. Status code: {response.status_code}. Response: {response.text}")

    


def get_project_name(project_id_str: str) -> str:
    access_token = get_access_token('wrike')
    # Here, you would usually make a GET request to Wrike API to fetch the folder name.
    # The request might look something like this:
    url = f"https://www.wrike.com/api/v4/folders/{project_id_str}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    # Suppose the response is a JSON object and status is one of the fields
    folder_name = response.json().get('data', {})[0].get("title")

    return folder_name


def get_project_info(project_id_str: str) -> dict: 
    access_token = get_access_token('wrike')
    # Here, you would usually make a GET request to Wrike API to fetch the folder name.
    # The request might look something like this:
    url = f"https://www.wrike.com/api/v4/folders/{project_id_str}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    # Suppose the response is a JSON object and status is one of the fields

    return response.json().get('data', {})[0]


def get_project_id(project_name_str: str) -> str:
    access_token = get_access_token('wrike')
    url = 'https://www.wrike.com/api/v4/folders?project=true'
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    project_id = find_dict(response.json(), 'title', project_name_str)
    if project_id is not None:
        print("project id obtained")
    return project_id
