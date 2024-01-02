import os.path
from PyQt6.QtWidgets import QMainWindow, QPushButton, QProgressBar
from googleapiclient.discovery import build
from constants import EMAIL_COUNT, SCOPES, USER_ID
from email_fetcher import EmailFetcherThread
from google_apis import authenticate

class MainWindow(QMainWindow):
    creds = None
    
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Email Fetcher')
        self.setGeometry(100, 100, 400, 200)

        self.button = QPushButton('Sync Emails', self)
        self.button.setGeometry(100, 60, 200, 40)

        self.progress = QProgressBar(self)
        self.progress.setGeometry(50, 120, 300, 20)

        self.button.clicked.connect(self.autenticate_and_fetch_emails)

    def syncEmails(self):
        print("fetching emails")
        email_service = build('gmail', 'v1', credentials=self.creds)
        sheets_service = build('sheets', 'v4', credentials=self.creds)
        
        results = email_service.users().messages().list(userId=USER_ID, maxResults=EMAIL_COUNT).execute()
        messages = results.get('messages', [])

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
    
    def autenticate_and_fetch_emails(self):
        self.creds = authenticate()
        self.syncEmails()