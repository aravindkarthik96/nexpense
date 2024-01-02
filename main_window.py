import os.path
from PyQt6.QtWidgets import QMainWindow, QPushButton, QProgressBar
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from constants import EMAIL_COUNT, SCOPES, USER_ID
from email_fetcher import EmailFetcherThread

class MainWindow(QMainWindow):
    creds = None
    
    def __init__(self,):
        super().__init__()

        self.setWindowTitle('Email Fetcher')
        self.setGeometry(100, 100, 400, 200)

        self.button = QPushButton('Sync Emails', self)
        self.button.setGeometry(100, 60, 200, 40)

        self.progress = QProgressBar(self)
        self.progress.setGeometry(50, 120, 300, 20)

        self.button.clicked.connect(self.autenticate_and_fetch_emails)

    def fetch_emails(self):
        print("fething emails")
        email_service = build('gmail', 'v1', credentials=self.creds)
        results = email_service.users().messages().list(userId=USER_ID, maxResults=EMAIL_COUNT).execute()
        messages = results.get('messages', [])
        
        sheets_service = build('sheets', 'v4', credentials=self.creds)

        if not messages:
            print("No messages found.")
            return

        # Set up and start the QThread for fetching emails
        self.progress.setMaximum(len(messages))
        self.progress.setValue(0)
        self.button.setDisabled(True)

        self.thread = EmailFetcherThread(email_service, sheets_service, messages)
        self.thread.update_progress.connect(self.update_progress)
        self.thread.finished.connect(self.fetching_complete)
        self.thread.start()

    def update_progress(self, value):
        self.progress.setValue(value)

    def fetching_complete(self):
        print(f"Completed syncing {EMAIL_COUNT} emails")
        self.button.setDisabled(False)
    
    def authenticate(self):
        print("authenticating")
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            print("already authenticated")
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
                print("refreshing authentication")
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
                print("refreshing authentication")
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())
    
    def autenticate_and_fetch_emails(self):
        self.authenticate()
        self.fetch_emails()