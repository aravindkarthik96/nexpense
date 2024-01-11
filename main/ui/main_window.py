from PyQt6.QtWidgets import QMainWindow, QPushButton, QProgressBar
from constants import EMAIL_COUNT, SHEET_ID, USER_ID
from main.google_apis.gmail_apis import get_email_serivce, get_message_ids
from main.google_apis.sheets_apis import (
    fetch_processed_transactions,
    get_sheets_serivce,
)
from main.processors.email_processor import EmailProcessorThread
from main.google_apis.auth_apis import authenticate
from main.processors.insights_processor import InsightsProcessorThread


class MainWindow(QMainWindow):
    creds = None

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Nexpense")
        self.setGeometry(50, 100, 400, 200)

        self.sync_button = QPushButton("Sync Emails", self)
        self.sync_button.setGeometry(50, 20, 300, 40)

        self.get_insights_button = QPushButton("Gather Insights", self)
        self.get_insights_button.setGeometry(50, 70, 300, 40)

        self.progress = QProgressBar(self)
        self.progress.setGeometry(50, 140, 300, 20)

        self.sync_button.clicked.connect(self.autenticate_and_fetch_emails)
        self.get_insights_button.clicked.connect(
            self.authenticate_and_get_insights_from_data
        )

    def syncEmails(self):
        self.processing_start()
        self.thread = EmailProcessorThread(creds=self.creds)
        self.thread.update_progress.connect(self.update_progress)
        self.thread.finished.connect(self.processing_complete)
        self.thread.start()

    def get_insights_from_data(self):
        self.processing_start()
        self.thread = InsightsProcessorThread(creds=self.creds)
        self.thread.update_progress.connect(self.update_progress)
        self.thread.finished.connect(self.processing_complete)
        self.thread.start()

    def update_progress(self, value):
        self.progress.setValue(value)

    def processing_start(self):
        self.reset_progress_bar()
        self.set_buttons_enabled_state(False)

    def processing_complete(self):
        print(f"Completed syncing {EMAIL_COUNT} emails")
        self.sync_button.setDisabled(False)
        self.get_insights_button.setDisabled(False)

    def autenticate_and_fetch_emails(self):
        self.creds = authenticate()
        self.syncEmails()

    def authenticate_and_get_insights_from_data(self):
        self.creds = authenticate()
        self.get_insights_from_data()

    def reset_progress_bar(self):
        self.progress.setMaximum(1)
        self.progress.setValue(0)

    def set_buttons_enabled_state(self, state: bool):
        self.sync_button.setDisabled(not (state))
        self.get_insights_button.setDisabled(not (state))
