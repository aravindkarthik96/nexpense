from constants import SHEET_ID
from PyQt6.QtCore import QThread, pyqtSignal
from main.google_apis.gmail_apis import get_mime_message
from main.google_apis.sheets_apis import (
    set_header_row,
    upload_processed_message_ids,
    upload_transactions_to_sheet,
    get_processed_message_ids,
)
import main.processors.message_parsers as mp


class EmailProcessorThread(QThread):
    update_progress = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, email_service, sheets_service, messages):
        super().__init__()
        self.email_service = email_service
        self.sheets_service = sheets_service
        self.messages = messages

    def run(self):
        transactions = []
        previously_processed_emails = get_processed_message_ids(
            self.sheets_service, SHEET_ID
        )

        set_header_row(previously_processed_emails, self.sheets_service, SHEET_ID)

        new_message_ids = []
        for idx, message in enumerate(self.messages):
            message_id = message["id"]
            self.update_progress.emit(idx + 1)

            if message_id in set(previously_processed_emails):
                print(f"skipping message {message_id}, already present in DB")
                continue

            new_message_ids.append(message_id)

            mime_message = get_mime_message(self.email_service, "me", message_id)

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
                f"Completed Fetching email #{idx} | Transactional: {transaction_email != None}"
            )

        upload_transactions_to_sheet(self.sheets_service, SHEET_ID, transactions)
        upload_processed_message_ids(self.sheets_service, SHEET_ID, new_message_ids)
        # Emit signal when finished
        self.finished.emit()
