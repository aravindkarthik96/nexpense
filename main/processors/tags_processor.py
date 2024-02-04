from constants import SHEET_ID
from PyQt6.QtCore import QThread, pyqtSignal

from main.google_apis.sheets_apis import (
    fetch_processed_transactions,
    get_sheets_serivce,
    set_tag_on_row,
)
import main.processors.message_parsers as mp


class TagsProcessorThread(QThread):
    finished = pyqtSignal()

    def __init__(self, creds, sheet_id, message_id, merchant_name, new_tag):
        super().__init__()
        self.creds = creds
        self.sheet_id = sheet_id
        self.message_id = message_id
        self.merchant_name = merchant_name
        self.new_tag = new_tag

    def on_thread_finished(self):
        print(f"Thread {self.sender()} finished and is being cleaned up")
        
    def run(self):
        print(f"Thread {self} started")
        sheets_api = get_sheets_serivce(self.creds)

        processedTransactions = fetch_processed_transactions(self.creds, self.sheet_id)
        
        print(f"finding transactions that match {self.message_id} with merchant name '{self.merchant_name}',new tag: '{self.new_tag}'")
        
        for row, transaction in enumerate(processedTransactions):
            
            try:
                current_tag = transaction[6]
            except IndexError:
                current_tag = None
            
            if (transaction[5] == self.merchant_name) & (
                (transaction[0] == self.message_id) | (current_tag == None)
            ):
                print(f"updating tag on row {row} with merchant name '{transaction[5]}', message id '{self.message_id}', existing tag '{current_tag}'")
                set_tag_on_row(sheets_api, SHEET_ID, row+2, self.new_tag)

        print(f"Processing complete, emitting result")
        
        print(f"Thread {self} finished")
        self.finished.emit()
        
