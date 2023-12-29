import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton

import os.path
import base64
import email
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email import message_from_bytes
import re

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_header(header_name, headers):
    """
    Fetches the header value for a given header name from a list of (Header, Value) tuples.
    """
    for name, value in headers:
        if name.lower() == header_name.lower():
            return value
    return None

def extract_hdfc_transaction_details(email_content):
    details = {
        'bank_name': 'HDFC Bank',  # Inferred from the email's context, as it's static in this case
        'transaction_amount': None,
        'merchant': None,
        'date_time': None
    }

    # Pattern for the transaction amount
    amount_pattern = r"Rs (\d+.\d+)"
    amount_match = re.search(amount_pattern, email_content)
    if amount_match:
        details['transaction_amount'] = amount_match.group(1)

    # Pattern for the merchant
    merchant_pattern = r"at (.*?) on"
    merchant_match = re.search(merchant_pattern, email_content)
    if merchant_match:
        details['merchant'] = merchant_match.group(1)

    # Pattern for the date & time
    date_time_pattern = r"on (\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2})"
    date_time_match = re.search(date_time_pattern, email_content)
    if date_time_match:
        details['date_time'] = date_time_match.group(1)

    return details

def extract_kotak_transaction_details(email_content):
    details = {
        'bank_name': 'Kotak Mahindra Bank Ltd',  # Inferred as static from the email context
        'transaction_amount': None,
        'merchant': None,
        'date_time': None
    }

    # Pattern for the transaction amount
    amount_pattern = r"A Transaction of INR (\d+.\d+)"
    amount_match = re.search(amount_pattern, email_content)
    if amount_match:
        details['transaction_amount'] = amount_match.group(1)

    # Pattern for the merchant
    merchant_pattern = r"at (.+?) on"
    merchant_match = re.search(merchant_pattern, email_content)
    if merchant_match:
        details['merchant'] = merchant_match.group(1)

    # Pattern for the date
    date_pattern = r"on (\d{2}-\w{3}-\d{4})"
    date_match = re.search(date_pattern, email_content)
    if date_match:
        details['date_time'] = date_match.group(1)

    return details

def extract_citibank_transaction_details(email_content):
    details = {
        'bank_name': 'Citibank',  # Known from the context
        'transaction_amount': None,
        'merchant': None,
        'date_time': None
    }

    # Pattern for the transaction amount
    amount_pattern = r"Rs\. (\d+(\.\d+)?)"
    amount_match = re.search(amount_pattern, email_content)
    if amount_match:
        details['transaction_amount'] = amount_match.group(1)

    # Pattern for the merchant
    merchant_pattern = r"at ([\w\s\-]+) on"
    merchant_match = re.search(merchant_pattern, email_content)
    if merchant_match:
        details['merchant'] = merchant_match.group(1).strip()

    # Pattern for the date & time
    date_pattern = r"on (\d{2}-\w{3}-\d{2})"
    date_match = re.search(date_pattern, email_content)
    if date_match:
        details['date_time'] = date_match.group(1)

    return details

def extract_citibank_upi_transaction_details(email_content):
    details = {
        'bank_name': 'Citibank',  # Known from the context
        'transaction_amount': None,
        'merchant': None,
        'date_time': None
    }

    # Pattern for the transaction amount
    amount_pattern = r"Rs\. (\d+(\.\d+)?)"
    amount_match = re.search(amount_pattern, email_content)
    if amount_match:
        details['transaction_amount'] = amount_match.group(1)

    # Pattern for the merchant
    merchant_pattern = r"at ([\w\s\-]+) on"
    merchant_match = re.search(merchant_pattern, email_content)
    if merchant_match:
        details['merchant'] = merchant_match.group(1).strip()

    # Pattern for the date & time
    date_pattern = r"on (\d{2}-\w{3}-\d{2})"
    date_match = re.search(date_pattern, email_content)
    if date_match:
        details['date_time'] = date_match.group(1)

    return details

def extract_citibank_upi_transaction_details_v2(email_content):
    details = {
        'bank_name': 'Citibank',  # Known from the context
        'transaction_amount': None,
        'merchant': None,
        'date_time': None
    }

    # Adjusted pattern for the transaction amount
    amount_pattern = r"INR (\d+(?:\.\d{1,2})?)"
    amount_match = re.search(amount_pattern, email_content)
    if amount_match:
        details['transaction_amount'] = amount_match.group(1)

    # Adjusted pattern for the date & time
    date_time_pattern = r"on (\d{2}-\w{3}-\d{2,4} at \d{2}:\d{2})"
    date_time_match = re.search(date_time_pattern, email_content)
    if date_time_match:
        details['date_time'] = date_time_match.group(1)

    # Adjusted pattern for merchant/UPI ID
    merchant_pattern = r"and account (.*?) has been credited"
    merchant_match = re.search(merchant_pattern, email_content)
    if merchant_match:
        details['merchant'] = merchant_match.group(1).strip()

    return details

    return details

def get_mime_message(service, user_id, msg_id):
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id, format='raw').execute()
        msg_raw = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
        mime_msg = email.message_from_bytes(msg_raw)
        return mime_msg
    except Exception as error:
        print(f'An error occurred: {error}')
        return None
        
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set some window properties
        self.setWindowTitle('Email Fetcher')
        self.setGeometry(100, 100, 400, 200)  # x, y, width, height

        # Create a QPushButton and set its properties
        self.button = QPushButton('Fetch Emails', self)
        self.button.setGeometry(100, 60, 200, 40)  # x, y, width, height

        # Connect the button to the function that will handle the email fetching
        self.button.clicked.connect(self.fetch_emails)
   
    def fetch_emails(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            # Call the Gmail API
            service = build('gmail', 'v1', credentials=creds)
            # Request a list of all the messages
            results = service.users().messages().list(userId='me', labelIds = ["CATEGORY_UPDATES"],maxResults=100).execute()
            
            messages = results.get('messages', [])

            if not messages:
                print("No messages found.")
                return
            print(f"found {len(messages)}")
    
            self.button.setDisabled = True
            
            for message in messages:
                mime_msg = get_mime_message(service, 'me', message['id'])
                if not mime_msg:
                    continue  # if the message couldn't be retrieved, skip it

                email_body = None
                if mime_msg.is_multipart():
                    for part in mime_msg.walk():
                        # Check the content type and ignore attachments
                        if part.get_content_type() in ["text/plain", "text/html"] and "attachment" not in part.get("Content-Disposition", ""):
                            email_body = part.get_payload(decode=True).decode()
                            break  # once the correct body is found, no need to continue looping
                else:
                    # if it is a simple email body, just get the payload
                    email_body = mime_msg.get_payload(decode=True).decode()
                
                # Ensure we have an email body to process
                if email_body:
                    subject = get_header("Subject", mime_msg.items())
                    
                    if subject == "Alert :  Update on your HDFC Bank Credit Card" :
                        print(extract_hdfc_transaction_details(email_body))
                    elif subject == "Kotak Bank Credit Card Transaction Alert" :
                        print(extract_kotak_transaction_details(email_body))
                    elif subject == "Citi Purchase Alert" :
                        print(extract_citibank_transaction_details(email_body))
                    elif subject == "CitiAlert - UPI Transaction Successful" :
                        print(extract_citibank_upi_transaction_details(email_body))
                    elif subject == "CitiAlert - UPI Fund Transfer Acknowledgement" :
                        print(extract_citibank_upi_transaction_details_v2(email_body))
                        
            print("Completed Fetching")
        except Exception as error:
            print(f'An error occurred: {error}')

# Initialize the application and create the GUI
app = QApplication(sys.argv)
mainWindow = MainWindow()
mainWindow.show()

# Run the application's main loop
sys.exit(app.exec())

