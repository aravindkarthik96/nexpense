import sys
import os.path
import base64
import email
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QProgressBar
from PyQt6.QtCore import QThread, pyqtSignal
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email import message_from_bytes
import message_parsers as mp

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
EMAIL_COUNT = 50
USER_ID = 'me'

def get_mime_message(service, user_id, msg_id):
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id, format='raw').execute()
        msg_raw = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
        mime_msg = email.message_from_bytes(msg_raw)
        return mime_msg

    except Exception as error:
        print(f'An error occurred: {error}')
        return None

class EmailFetcherThread(QThread):
    update_progress = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, service, messages):
        super().__init__()
        self.service = service
        self.messages = messages

    def run(self):
        for idx, message in enumerate(self.messages):
            mime_msg = get_mime_message(self.service, 'me', message['id'])
            if not mime_msg:
                continue  # if the message couldn't be retrieved, skip it
            # Now let's handle the MIME message to get the email body and subject
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
                
                if subject == "Alert :  Update on your HDFC Bank Credit Card" :
                    print(mp.extract_hdfc_transaction_details(email_body))
                elif subject == "Kotak Bank Credit Card Transaction Alert" :
                    print(mp.extract_kotak_transaction_details(email_body))
                elif subject == "Citi Purchase Alert" :
                    print(mp.extract_citibank_transaction_details(email_body))
                elif subject == "CitiAlert - UPI Transaction Successful" :
                    print(mp.extract_citibank_upi_transaction_details(email_body))
                elif subject == "CitiAlert - UPI Fund Transfer Acknowledgement" :
                    print(mp.extract_citibank_upi_transaction_details_v2(email_body))
                
            print(f"Completed Fetching email #{idx}")
            self.update_progress.emit(idx + 1)

        # Emit signal when finished
        self.finished.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Email Fetcher')
        self.setGeometry(100, 100, 400, 200)

        self.button = QPushButton('Sync Emails', self)
        self.button.setGeometry(100, 60, 200, 40)

        self.progress = QProgressBar(self)
        self.progress.setGeometry(50, 120, 300, 20)

        self.button.clicked.connect(self.fetch_emails)

    def fetch_emails(self):
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId=USER_ID, maxResults=EMAIL_COUNT).execute()
        messages = results.get('messages', [])

        if not messages:
            print("No messages found.")
            return

        # Set up and start the QThread for fetching emails
        self.progress.setMaximum(len(messages))
        self.progress.setValue(0)
        self.button.setDisabled(True)

        self.thread = EmailFetcherThread(service, messages)
        self.thread.update_progress.connect(self.update_progress)
        self.thread.finished.connect(self.fetching_complete)
        self.thread.start()

    def update_progress(self, value):
        self.progress.setValue(value)

    def fetching_complete(self):
        print(f"Completed syncing {EMAIL_COUNT} emails")
        self.button.setDisabled(False)

app = QApplication(sys.argv)
mainWindow = MainWindow()
mainWindow.show()
sys.exit(app.exec())
