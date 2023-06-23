from __future__ import print_function

from datetime import datetime, timedelta
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from logger import Logger

class Gmail:
    def __init__(self, Logger) -> None:
        self.Logger = Logger
        self.SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        self.events_list = []
        self.Logger.info("Gmail calendar instantiated!")

    def GetEvents(self):
        creds = None
        root_directory = os.path.dirname(os.path.abspath(__file__)).split("src")[0]
        token_file = os.path.join(root_directory , 'src','data','token.json')
        cred_file = os.path.join(root_directory , 'src','data','credentials.json')

        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(cred_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_file, 'w') as token:
                token.write(creds.to_json())

        try:
            service = build('calendar', 'v3', credentials=creds)

            # Call the Calendar API
            now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            self.Logger.info('Gmail: Getting events!')
            events_result = service.events().list(calendarId='primary', timeMin=now,maxResults=10, singleEvents=True,orderBy='startTime').execute()
            events = events_result.get('items', [])

            if not events:
                return

            
            for event in events:
                if event['summary'] == "Gym":
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    datetime_object = datetime.fromisoformat(start)
                    self.Logger.info("Found Gym Event! " + str(datetime_object.date()))
                    self.events_list.append(datetime_object.date())

        except HttpError as error:
            self.Logger.warning('An error occurred: %s' % error)

    def FilterRelevantEvent(self):
        gym_event = None
        tomorrow =  datetime.now() + timedelta(days=1)

        for event in self.events_list:
            if event == tomorrow.date():
                gym_event = event
                self.Logger.info("Gym Event is tomorrow! " + str(event))
        
        return gym_event

if __name__ == '__main__':
    logger = Logger()
    mail = Gmail(logger)
    mail.GetEvents()
    event = mail.FilterRelevantEvent()

    