import json
from pathlib import Path

# Objects translator

# Define the path from index

path_objects_translator = Path(Path.cwd() / 'Components' / 'Translators' / 'objectsTranslator.json')

# Ensure the directory exists
path_objects_translator.parent.mkdir(parents=True, exist_ok=True)


def get_objects_translator():
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


def update_objects_translator(hubspot_id_str, wrike_id_str):
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


def get_status_translator():
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


def update_status_translator(hubspot_id_str, wrike_id_str):
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
