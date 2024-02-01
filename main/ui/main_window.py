from PyQt6.QtWidgets import QMainWindow, QPushButton, QProgressBar, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from PyQt6.QtGui import QColor
from constants import EMAIL_COUNT, SHEET_ID
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
        self.setGeometry(50, 100, 600, 400)  # Adjusted for extra content

        layout = QVBoxLayout()

        self.table = QTableWidget(self)
        self.table.setColumnCount(4)  # Merchant, Expense, Bank, Memo
        self.table.setHorizontalHeaderLabels(["Date", "Merchant name", "Bank", "Amount"])
        layout.addWidget(self.table)

        self.sync_button = QPushButton("Refresh Emails")
        layout.addWidget(self.sync_button)

        self.get_insights_button = QPushButton("Gather Insights")
        layout.addWidget(self.get_insights_button)

        self.progress = QProgressBar(self)
        layout.addWidget(self.progress)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.showFullScreen()
        
        self.sync_button.clicked.connect(self.autenticate_and_fetch_emails)
        self.get_insights_button.clicked.connect(self.authenticate_and_get_insights_from_data)
        self.autenticate_and_fetch_emails()

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
        self.display_transactions(fetch_processed_transactions(self.creds,spreadsheet_id=SHEET_ID))

    def authenticate_and_get_insights_from_data(self):
        self.creds = authenticate()
        self.get_insights_from_data()

    def reset_progress_bar(self):
        self.progress.setMaximum(1)
        self.progress.setValue(0)

    def set_buttons_enabled_state(self, state: bool):
        self.sync_button.setDisabled(not (state))
        self.get_insights_button.setDisabled(not (state))
        
    def display_transactions(self, transactions):
        self.table.setRowCount(len(transactions))
        for row, transaction in enumerate(transactions):
            is_debit = transaction[4] == 'debit'
            
            date_item = QTableWidgetItem(transaction[1])
            merchant_item = QTableWidgetItem(str(transaction[5]))
            bank_item = QTableWidgetItem(transaction[2])
            amount_item = QTableWidgetItem(transaction[3])
            
            color = QColor(188, 99, 99) if is_debit else QColor(99, 188, 99)
            
            for item in [merchant_item, date_item, bank_item, amount_item]:
                item.setBackground(color)
            
            self.table.scrollToBottom()
            
        
            self.table.setItem(row, 0, date_item)
            self.table.setItem(row, 1, merchant_item)
            self.table.setItem(row, 2, bank_item)
            self.table.setItem(row, 3, amount_item)
        