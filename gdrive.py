from Google import Create_Service
from typing import Optional

CLIENT_SECRET_FILE = 'Components/Credentials/credentials.json'
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)


def copy_folder_to(source_folder_id: str, source_drive_id: str, destination_folder_id: str, destination_drive_id: str, project_name: str) -> str:
    '''returns the id of the new copy'''
    # Call the Drive v3 API
    source_folder_id = str(source_folder_id)
    source_folder_metadata = service.files().get(fileId=source_folder_id, supportsAllDrives=True).execute()
    destination_folder_metadata = {
        'name': project_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [destination_folder_id]
    }

    search_folders = service.files().list(
        q=f"'{destination_folder_id}' in parents and trashed=false", fields="files(id, name)", corpora='drive', driveId=destination_drive_id,
        supportsAllDrives=True, includeItemsFromAllDrives=True).execute()
    list_of_folders = search_folders.get('files', [])
    print(list_of_folders)

    if project_name not in [i['name'] for i in list_of_folders]:
        destination_folder = service.files().create(body=destination_folder_metadata,
                                                    fields='id',
                                                    supportsAllDrives=True).execute()

        results = service.files().list(
            q=f"'{source_folder_id}' in parents", fields="files(id, name)", corpora='drive', driveId=source_drive_id,
            supportsAllDrives=True, includeItemsFromAllDrives=True).execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
        else:
            print('Files:')
            search_files = service.files().list(
                q=f"'{destination_folder['id']}' in parents and trashed=false",
                fields="files(id, name)",
                corpora='drive',
                driveId=destination_drive_id,
                supportsAllDrives=True, includeItemsFromAllDrives=True).execute()
            list_of_files = search_files.get('files', [])
            for item in items:
                metadata = []
                folder_metadata = []
                print(u'{0} ({1})'.format(item['name'], item['id']))
                metadata = service.files().get(fileId=item['id'], supportsAllDrives=True).execute()
                root_folder_id = destination_folder['id']
                if metadata['mimeType'] == 'application/vnd.google-apps.folder':
                    folder_metadata = {
                        'name': metadata['name'],
                        'mimeType': 'application/vnd.google-apps.folder',
                        'parents': [root_folder_id]
                    }
                    copy_folder_to(metadata['id'], source_drive_id, root_folder_id, destination_drive_id,
                                   metadata['name'])
                else:
                    if item['name'] not in [i['name'] for i in list_of_files]:
                        try:
                            file = service.files().copy(fileId=item['id'], body={"parents": [destination_folder['id']]},
                                                        supportsAllDrives=True).execute()
                        except Exception as e:
                            print('An unexpected error occurred', e)
                    else:
                        print('file already exist')
        return destination_folder['id']
    else:
        print('folder already exist')
        return None


# copy_folder_to('1_0pk9JF2y9xkOiJCMmfoJp8RHRHZlvzU', '0AIYZe1bK2f__Uk9PVA', '1k1pcBfoXmLq6WlRPCF0AjQi4VxTK0uUB',
# '0AIYZe1bK2f__Uk9PVA', 'clone')


def move_file(file_id: str, to_id: str) -> None:
    try:
        file = service.files().get(fileId=file_id,
                                   supportsAllDrives=True,
                                   fields='parents').execute()
        old_parents = ",".join(file.get('parents'))
        print(file)
        print(old_parents)
        file = (service.files().update(fileId=file_id,
                                       addParents=to_id,
                                       removeParents=old_parents,
                                       supportsAllDrives=True,
                                       fields='id, parents').execute()
                )
        print('file moved')
        print(file.get('parents'))
    except Exception as e:
        print('an unexpected error occurred', e)



def create_folder(parent_id: str, folder_name: str) -> Optional[str]:
    ''' returns an id'''
    destination_folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    try:
        destination_folder = service.files().create(body=destination_folder_metadata,
                                                        fields='id',
                                                        supportsAllDrives=True).execute()
        return str(destination_folder['id'])
    except Exception as e:
        print(f"An unexpected error occurred creating the folder: {e}")