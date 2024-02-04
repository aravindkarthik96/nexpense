from PyQt6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QProgressBar,
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
)
from PyQt6.QtGui import QColor
from constants import EMAIL_COUNT, SHEET_ID
from main.google_apis.gmail_apis import get_email_serivce, get_message_ids
from main.google_apis.sheets_apis import (
    fetch_processed_transactions,
)
from PyQt6.QtCore import Qt
from main.processors.email_processor import EmailProcessorThread
from main.google_apis.auth_apis import authenticate
from main.processors.insights_processor import InsightsProcessorThread
from main.processors.tags_processor import TagsProcessorThread
from main.ui.tags_dialogue import TagsDialog


class MainWindow(QMainWindow):
    creds = None

    def __init__(self):
        super().__init__()
        self.threads = {}
        self.setWindowTitle("Nexpense")
        self.setGeometry(50, 100, 600, 400)

        layout = QVBoxLayout()
        labels = ["Date", "Merchant name", "Bank name", "Amount", "Tag"]
        self.table = QTableWidget(self)
        self.table.setColumnCount(len(labels))
        self.table.setHorizontalHeaderLabels(labels)
        layout.addWidget(self.table)

        buttonsLayout = QHBoxLayout()

        self.sync_button = QPushButton("Sync Emails")
        buttonsLayout.addWidget(self.sync_button)

        self.get_insights_button = QPushButton("Gather Insights")
        buttonsLayout.addWidget(self.get_insights_button)

        self.update_tags_button = QPushButton("Update tags")
        buttonsLayout.addWidget(self.update_tags_button)

        layout.addLayout(buttonsLayout)

        self.progress = QProgressBar(self)
        layout.addWidget(self.progress)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.sync_button.clicked.connect(self.autenticate_and_fetch_emails)
        self.get_insights_button.clicked.connect(
            self.authenticate_and_get_insights_from_data
        )
        self.update_tags_button.clicked.connect(self.show_update_tags_dialog)
        self.autenticate_and_fetch_emails()
        self.table.itemChanged.connect(self.on_item_changed)

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
        self.display_transactions(
            fetch_processed_transactions(self.creds, spreadsheet_id=SHEET_ID)
        )

    def authenticate_and_get_insights_from_data(self):
        self.creds = authenticate()
        self.get_insights_from_data()

    def reset_progress_bar(self):
        self.progress.setMaximum(1)
        self.progress.setValue(0)

    def set_buttons_enabled_state(self, state: bool):
        self.sync_button.setDisabled(not (state))
        self.get_insights_button.setDisabled(not (state))

    def on_item_changed(self, item):
        print("item changed" + str(item))

    def display_transactions(self, transactions):
        self.table.setRowCount(len(transactions))
        for row, transaction in enumerate(transactions):
            is_debit = transaction[4] == "debit"
            tag_combobox = QComboBox()
            current_tag = transaction[6]
            tag_combobox.addItems(["Food Orders", "Hobbies", "Utilities", "Transport"])

            tag_index = tag_combobox.findText(current_tag)
            if tag_index >= 0:
                tag_combobox.setCurrentIndex(tag_index)
            else:
                tag_combobox.addItems([current_tag])
                tag_combobox.setCurrentIndex(tag_combobox.findText(current_tag))

            tag_combobox.currentIndexChanged.connect(
                lambda index, row=row, combobox=tag_combobox, message_id=transaction[
                    0
                ], merchant_name=transaction[5]: self.on_tag_changed(
                    message_id,
                    combobox.currentText(),
                    merchant_name,
                )
            )

            columns = [
                QTableWidgetItem(transaction[1]),
                QTableWidgetItem(str(transaction[5])),
                QTableWidgetItem(transaction[2]),
                QTableWidgetItem(transaction[3]),
            ]

            color: QColor = QColor(188, 99, 99) if is_debit else QColor(99, 188, 99)

            for index, column in enumerate(columns):
                column.setBackground(color)
                column.setFlags(
                    Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
                )
                self.table.setItem(row, index, column)

            self.table.setCellWidget(row, 4, tag_combobox)

            self.table.scrollToBottom()

    def on_tag_changed(self, message_id, new_tag, merchant_name):
        thread = TagsProcessorThread(
            self.creds, SHEET_ID, message_id, merchant_name, new_tag
        )
        thread_id = id(thread)
        self.threads[thread_id] = thread
        # self.syncEmails()
        # thread.finished.connect(lambda: self.on_thread_finished(thread_id))
        thread.start()

    def on_thread_finished(self, thread_id):
        if thread_id in self.threads:
            thread = self.threads.pop(thread_id)
            thread.deleteLater()
            
    def show_update_tags_dialog(self):
        tags = ["Tag1", "Tag2", "Tag3"]  # Replace with your actual tags list
        dialog = TagsDialog(tags, self)
        dialog.exec()  # Show the dialog as a modal window
