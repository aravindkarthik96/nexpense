from constants import EMAIL_COUNT, SHEET_ID, USER_ID
from PyQt6.QtCore import QThread, pyqtSignal
from main.google_apis.gmail_apis import get_email_serivce, get_message_ids, get_mime_message
from main.google_apis.sheets_apis import (
    get_sheets_serivce,
    set_header_row,
    upload_processed_message_ids,
    upload_transactions_to_sheet,
    get_processed_message_ids,
)
import main.processors.message_parsers as mp


class EmailProcessorThread(QThread):
    update_progress = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, creds):
        super().__init__()
        self.creds = creds

    def run(self):
        print("fetching emails")
        email_service = get_email_serivce(self.creds)
        sheets_service = get_sheets_serivce(self.creds)
        messages = get_message_ids(email_service, USER_ID, EMAIL_COUNT)

        if not messages:
            print("No messages found.")
            return
        transactions = []
        previously_processed_emails = get_processed_message_ids(
            sheets_service, SHEET_ID
        )

        set_header_row(previously_processed_emails, sheets_service, SHEET_ID)

        new_message_ids = []
        message_count = len(messages)
        
        for index, message in enumerate(messages):
            message_id = message["id"]
            self.update_progress.emit((index / message_count)*100)

            if message_id in set(previously_processed_emails):
                print(f"skipping message {message_id}, already present in DB")
                continue

            new_message_ids.append(message_id)

            mime_message = get_mime_message(email_service, "me", message_id)

            if not mime_message:
                continue

            email_body, subject = None, None

            email_body = mp.get_message_body(mime_message)

            if email_body:
                subject = mp.get_header("Subject", mime_message.items())
                transaction_email = None
                if subject == "Alert :  Update on your HDFC Bank Credit Card":
                    transaction_email = mp.extract_hdfc_transaction_details(email_body)
                elif subject == "Kotak Bank Credit Card Transaction Alert":
                    transaction_email = mp.extract_kotak_transaction_details(email_body)
                elif subject == "Citi Purchase Alert":
                    transaction_email = mp.extract_citibank_transaction_details(
                        email_body
                    )
                elif subject == "CitiAlert - UPI Transaction Successful":
                    transaction_email = mp.extract_citibank_upi_transaction_details(
                        email_body
                    )
                elif subject == "CitiAlert - UPI Fund Transfer Acknowledgement":
                    transaction_email = mp.extract_citibank_upi_transaction_details_v2(
                        email_body
                    )

                if transaction_email != None:
                    transaction_email["message_id"] = message_id
                    transaction_email["date_time"] = mp.format_date(
                        mp.get_header("Date", mime_message.items())
                    )
                    transactions.append(transaction_email)

            print(
                f"Completed Fetching email #{index} | Transactional: {transaction_email != None}"
            )

        upload_transactions_to_sheet(sheets_service, SHEET_ID, transactions)
        upload_processed_message_ids(sheets_service, SHEET_ID, new_message_ids)
        # Emit signal when finished
        self.finished.emit()
