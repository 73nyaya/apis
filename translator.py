import json
from pathlib import Path
from enum import Enum

# data class translators

class Translators(Enum):
    objects: str = 'objectsTranslator' # relation between deal ids and project ids
    folders: str = 'foldersTranslator' # rleation between project ids and offer folder in marketing and sales
    customer_folders: str = 'customerFoldersTranslator' # relation between customer custom field in wrike and the customer folder in the engineering space/projects
    project_folders: str = 'projectFoldersTranslator'# relation between project ids and project folders in the engineering space/customer folder
    folder_types: str = 'folderTypesTranslator' # relation between project types (custom field in wrike) and folder templates id from drive
    status: str = 'statusTranslator' # relation between status ids of deal stages and status ids in wrike

# Objects translator

# Define the path from index


path_objects_translator = Path(Path.cwd() / 'Components' / 'Translators' / 'objectsTranslator.json')
path_folders_translator = Path(Path.cwd() / 'Components' / 'Translators' / 'foldersTranslator.json')

# Ensure the directory exists
path_objects_translator.parent.mkdir(parents=True, exist_ok=True)
path_folders_translator.parent.mkdir(parents=True, exist_ok=True)


def get_translator(translator_case: Translators) -> dict:
    path_translator = Path(Path.cwd() / 'Components' / 'Translators' / translator_case+'.json')
    path_translator.mkdir(parents=True, exist_ok=True)
    try:
        with open(path_translator, 'r') as f:
            translator = json.load(f)
        return translator

    except FileNotFoundError:
        translator = {}
        with open(path_translator, 'w') as f:
            json.dump(translator, f)
        print('objects translator has been created successfully.')
        return translator

    except Exception as e:
        print('Exception', e)    

def update_translator(translator_case: str, key: str, value: str) -> None:
    path_translator = Path(Path.cwd() / 'Components' / 'Translators' / translator_case+'.json')
    path_translator.mkdir(parents=True, exist_ok=True)
    # Load existing data
    try:
        with open(path_translator, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    # Check if the value exists
    if key not in data.keys():
        # Add new key-value pair
        data[key] = value

    # Write back to file
    with open(path_translator, 'w') as f:
        json.dump(data, f, indent=4)

def delete_translator_record(translator_case: str, key: str):
    path_translator = Path(Path.cwd() / 'Components' / 'Translators' / translator_case+'.json')
    # Load existing data
    try:
        with open(path_translator, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    # Check if the value exists
    if key in data.keys():
        # Add new key-value pair
        del data[key]

    # Write back to file
    with open(path_translator, 'w') as f:
        json.dump(data, f, indent=4)


def get_objects_translator() -> dict:
    try:
        with open(path_objects_translator, 'r') as f:
            objects_translator = json.load(f)
        return objects_translator

    except FileNotFoundError:
        objects_translator = {}
        with open(path_objects_translator, 'w') as f:
            json.dump(objects_translator, f)
        print('objects translator has been created successfully.')
        return objects_translator

    except Exception as e:
        print('Exception', e)


def update_objects_translator(hubspot_id_str: str, wrike_id_str: str) -> None:
    # Load existing data
    try:
        with open(path_objects_translator, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    # Check if the value exists
    if hubspot_id_str not in data.keys():
        # Add new key-value pair
        data[hubspot_id_str] = wrike_id_str

    # Write back to file
    with open(path_objects_translator, 'w') as f:
        json.dump(data, f, indent=4)


# Stage Status translator

# Define the path from index

path_status_translator = Path(Path.cwd() / 'Components' / 'Translators' / 'statusTranslator.json')

# Ensure the directory exists
path_status_translator.parent.mkdir(parents=True, exist_ok=True)


def get_status_translator() -> dict:
    try:
        with open(path_status_translator, 'r') as f:
            status_translator = json.load(f)
        return status_translator

    except FileNotFoundError:
        status_translator = {'appointmentscheduled': 'IEAEINT7JMCLXA5I',
                             'decisionmakerboughtin': 'IEAEINT7JMEFQTGG',
                             '184967120': 'IEAEINT7JMCLXA7E',
                             '194277368': 'IEAEINT7JMCLXA7O',
                             'contractsent': 'IEAEINT7JMCLXA7Y',
                             'closedwon': 'IEAEINT7JMCLXBAC',
                             'closedlost': 'IEAEINT7JMCLXBBD',
                             '194277369': 'IEAEINT7JMD76XV3'}
        with open(path_status_translator, 'w') as f:
            json.dump(status_translator, f)
        print('status translator has been created successfully.')
        return status_translator

    except Exception as e:
        print('Exception', e)


def update_status_translator(hubspot_id_str: str, wrike_id_str: str) -> None:
    # Load existing data
    try:
        with open(path_status_translator, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    # Check if the value exists
    if hubspot_id_str not in data.keys():
        # Add new key-value pair
        data[hubspot_id_str] = wrike_id_str

    # Write back to file
    with open(path_status_translator, 'w') as f:
        json.dump(data, f, indent=4)


def get_status_names():
    with open(path_status_translator, 'r') as f:
        data = json.load(f)
        return data.keys()


def delete_object_record(deal_id):
    # Load existing data
    try:
        with open(path_objects_translator, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    # Check if the value exists
    if deal_id in data.keys():
        # Add new key-value pair
        del data[deal_id]

    # Write back to file
    with open(path_objects_translator, 'w') as f:
        json.dump(data, f, indent=4)


def get_folders_translator():
    try:
        with open(path_folders_translator, 'r') as f:
            folders_translator = json.load(f)
        return folders_translator

    except FileNotFoundError:
        folders_translator = {}
        with open(path_folders_translator, 'w') as f:
            json.dump(folders_translator, f)
        print('objects translator has been created successfully.')
        return folders_translator

    except Exception as e:
        print('Exception', e)

def update_folders_translator(wrike_id_str, gdrive_id_str):
    # Load existing data
    try:
        with open(path_folders_translator, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    # Check if the value exists
    if wrike_id_str not in data.keys():
        # Add new key-value pair
        data[wrike_id_str] = gdrive_id_str

    # Write back to file
    with open(path_folders_translator, 'w') as f:
        json.dump(data, f, indent=4)

def delete_folder_record(project_id):
    # Load existing data
    try:
        with open(path_folders_translator, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    # Check if the value exists
    if project_id in data.keys():
        # Add new key-value pair
        del data[project_id]

    # Write back to file
    with open(path_folders_translator, 'w') as f:
        json.dump(data, f, indent=4)