from PyQt6.QtWidgets import QMainWindow, QPushButton, QProgressBar
from constants import EMAIL_COUNT, USER_ID
from main.google_apis.gmail_apis import get_email_serivce, get_message_ids
from main.google_apis.sheets_apis import get_sheets_serivce
from main.processors.email_processor import EmailProcessorThread
from main.google_apis.auth_apis import authenticate

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
        email_service = get_email_serivce(self.creds)
        sheets_service = get_sheets_serivce(self.creds)
        
        messages = get_message_ids(email_service, USER_ID, EMAIL_COUNT)

        if not messages:
            print("No messages found.")
            return

        self.progress.setMaximum(len(messages))
        self.progress.setValue(0)
        self.button.setDisabled(True)

        self.thread = EmailProcessorThread(email_service, sheets_service, messages)
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