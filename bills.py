from __future__ import print_function
import httplib2
import os
import sys
from optparse import OptionParser
from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
import datetime
import calendar

SCOPES = 'https://www.googleapis.com/auth/tasks https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'tasks.json'
APPLICATION_NAME = 'Bill Checklist'
BILLS_CALENDAR_ID = 'grm70h5srpq90vp7v6upsaoce4@group.calendar.google.com'

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

def get_task_service():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    return discovery.build('tasks', 'v1', http=http)

def get_calendar_service():
     credentials = get_credentials()
     http = credentials.authorize(httplib2.Http())
     return discovery.build('calendar', 'v3', http=http)

def list_all_tasks():
    service = get_task_service()
    results = service.tasklists().list(maxResults=10).execute()
    items = results.get('items', [])
    if not items:
        print('No task lists found.')
    else:
        print('Task lists:')
        for item in items:
            print('{0} ({1})'.format(item['title'], item['id']))
   
def create_task_list(month, year):
    service = get_task_service()

    label_month = datetime.date(year, month, 1)

    tasklist_details = {
        'title': 'Bills for {0:%B}'.format(label_month) 
    }

    tasklist = service.tasklists().insert(body=tasklist_details).execute()
    
    bills = get_all_bills(month, year)
    bills.reverse()

    for bill in bills:
        task_details = {
            'title': '{0} ({1})'.format(bill['summary'], bill['start']['date']),
            'due'  : '{0}T00:00:00Z'.format(bill['start']['date'])
        }

        service.tasks().insert(tasklist=tasklist['id'], body=task_details).execute()    

def get_all_bills(month, year):
    (first_week_day, number_of_days) = calendar.monthrange(year, month)
    start_date = datetime.date(year, month, 1)
    end_date   = datetime.date(year, month, number_of_days)

    service = get_calendar_service()
    
    timeMin = '{0:%Y}-{0:%m}-{0:%d}T00:00:00Z'.format(start_date)
    timeMax = '{0:%Y}-{0:%m}-{0:%d}T00:00:00Z'.format(end_date)
    results = service.events().list(calendarId=BILLS_CALENDAR_ID, timeMin=timeMin, timeMax=timeMax, singleEvents=True).execute()
    events = results.get('items', [])
  
    return sorted(events, key=lambda e: e['start']['date'])

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('-y', '--year', dest='year',
        help='Year for bill checklist')

    parser.add_option('-m', '--month', dest='month',
        help='Month for bill checklist')

    (options, args) = parser.parse_args()

    if not options.year or not options.month:
        print("Year and month required")
        sys.exit(1)

    create_task_list(int(options.month), int(options.year))

