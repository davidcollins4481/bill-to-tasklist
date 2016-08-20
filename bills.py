
from __future__ import print_function
import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/tasks'
CLIENT_SECRET_FILE = 'tasks.json'
APPLICATION_NAME = 'Bill Checklist'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.googleapi')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'billtodolist.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def get_service():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    return discovery.build('tasks', 'v1', http=http)

def list_all_tasks():
    service = get_service()
    results = service.tasklists().list(maxResults=10).execute()
    items = results.get('items', [])
    if not items:
        print('No task lists found.')
    else:
        print('Task lists:')
        for item in items:
            print('{0} ({1})'.format(item['title'], item['id']))
   
def create_task_list():
    service = get_service()
    tasklist_details = {
        'title': 'todays list'
    }

    tasklist = service.tasklists().insert(body=tasklist_details).execute()
    
    task_details = {
        'title': 'New Task',
        'notes': 'Please complete me',
        'due': '2017-10-15T12:00:00.000Z'
    }    
    
    task = service.tasks().insert(tasklist=tasklist['id'], body=task_details).execute()
    print(task)

def main():
    #create_task_list()
    #list_all_tasks()

if __name__ == '__main__':
    main()
