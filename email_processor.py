from constants import SHEET_ID
from PyQt6.QtCore import QThread, pyqtSignal
from google_apis import get_mime_message, get_processed_message_ids, upload_processed_message_ids, upload_transactions_to_sheet
import message_parsers as mp

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
        previously_processed_emails = get_processed_message_ids(self.sheets_service,SHEET_ID)
        new_message_ids = []
        for idx, message in enumerate(self.messages):
            message_id = message['id']
            new_message_ids.append(message_id)
            
            if message_id in set(previously_processed_emails) :
                print(f"skipping message {message_id}, already present in DB")
                continue
            
            mime_msg = get_mime_message(self.email_service, 'me', message_id)

            if not mime_msg:
                continue  

            email_body, subject = None, None
        
            # Decode the subject and body
            for header, value in mime_msg.items():
                if header.lower() == 'subject':
                    subject = value
            
            if mime_msg.is_multipart():
                for part in mime_msg.walk():
                    if part.get_content_type() in ["text/plain", "text/html"]:
                        charset = part.get_content_charset()
                        try:
                            email_body = part.get_payload(decode=True).decode(charset or 'utf-8')
                        except UnicodeDecodeError:
                            email_body = part.get_payload(decode=True).decode('iso-8859-1', errors='replace')
                        break  # once the correct body is found, no need to continue looping
            else:
                charset = mime_msg.get_content_charset()
                try:
                    email_body = mime_msg.get_payload(decode=True).decode(charset or 'utf-8')
                except UnicodeDecodeError:
                    email_body = mime_msg.get_payload(decode=True).decode('iso-8859-1', errors='replace')
            
            # Ensure we have an email body to process
            if email_body:
                subject = mp.get_header("Subject", mime_msg.items())
                transaction_email = None
                if subject == "Alert :  Update on your HDFC Bank Credit Card" :
                    transaction_email = mp.extract_hdfc_transaction_details(email_body)
                elif subject == "Kotak Bank Credit Card Transaction Alert" :
                    transaction_email = mp.extract_kotak_transaction_details(email_body)
                elif subject == "Citi Purchase Alert" :
                    transaction_email = mp.extract_citibank_transaction_details(email_body)
                elif subject == "CitiAlert - UPI Transaction Successful" :
                    transaction_email = mp.extract_citibank_upi_transaction_details(email_body)
                elif subject == "CitiAlert - UPI Fund Transfer Acknowledgement" :
                    transaction_email = mp.extract_citibank_upi_transaction_details_v2(email_body)
                
                if transaction_email != None :
                    transaction_email['message_id'] = message_id
                    transactions.append(transaction_email)
                    print(transaction_email)
                
            print(f"Completed Fetching email #{idx}")
            self.update_progress.emit(idx + 1)

        upload_transactions_to_sheet(self.sheets_service,SHEET_ID,transactions)
        
        
        upload_processed_message_ids(self.sheets_service,SHEET_ID,new_message_ids)
        # Emit signal when finished
        self.finished.emit()
