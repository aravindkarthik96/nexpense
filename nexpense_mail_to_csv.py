import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton

import os.path
import base64
import email
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set some window properties
        self.setWindowTitle('Email Fetcher')
        self.setGeometry(100, 100, 400, 200)  # x, y, width, height

        # Create a QPushButton and set its properties
        self.button = QPushButton('Fetch Emails', self)
        self.button.setGeometry(100, 60, 200, 40)  # x, y, width, height

        # Connect the button to the function that will handle the email fetching
        self.button.clicked.connect(self.fetch_emails)

    def fetch_emails(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            # Call the Gmail API
            service = build('gmail', 'v1', credentials=creds)
            # Request a list of all the messages
            results = service.users().messages().list(userId='me', labelIds = [],maxResults=100).execute()
            messages = results.get('messages', [])

            if not messages:
                print("No messages found.")
                return
            print(f"found {len(messages)}")

            # Fetch each message and process it
            for message in messages[:5]:  # Retrieve only the first 5 messages for demo purposes
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                print(msg['snippet'])
                # You can add here more processing logic to parse the email and extract needed data

        except Exception as error:
            print(f'An error occurred: {error}')


# Initialize the application and create the GUI
app = QApplication(sys.argv)
mainWindow = MainWindow()
mainWindow.show()

# Run the application's main loop
sys.exit(app.exec())

