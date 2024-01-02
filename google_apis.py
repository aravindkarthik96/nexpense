import base64
import email
import os

from httplib2 import Credentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from requests import HTTPError

from constants import SCOPES

def upload_processed_message_ids(sheets_service,spreadsheet_id, message_ids):
    print(f"Uploading processed messages")
    values = []
    
    for message_id in message_ids :
        values.append([message_id])
    
    body = {
        'values': values
    }
    
    result = sheets_service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range="Sheet2",
        valueInputOption="USER_ENTERED",
        body=body).execute()
    print(f"{result.get('updates').get('updatedCells')} cells appended.")

def upload_transactions_to_sheet(sheets_service, spreadsheet_id, transactions):
    print(f"Uploading emails to sheets {len(transactions)}")
    # Prepare the data to upload
    # values = [["MessageID","Date","Bank", "Amount", "Type", "Merchant"]]  # Your header row
    values = []
    for transaction in transactions:
        try:
            # Convert the JSON string into a Python dictionary
            transaction_json = transaction

            values.append([
            transaction_json["message_id"],
            transaction_json["date_time"],
            transaction_json['bank_name'],
            transaction_json['transaction_amount'],
            transaction_json['type'],
            transaction_json['merchant']
        ])
            
        except Exception as error:
            print(f"Invalid JSON string - message: {transaction} error: {error}")
            return "Invalid JSON string"

    body = {
        'values': values
    }

    # Use the Sheets API to append the data
    result = sheets_service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range="Sheet1",  # Adjust if your sheet is named differently
        valueInputOption="USER_ENTERED",
        body=body).execute()
    print(f"{result.get('updates').get('updatedCells')} cells appended.")

def get_mime_message(email_service, user_id, msg_id):
    try:
        message = email_service.users().messages().get(userId=user_id, id=msg_id, format='raw').execute()
        msg_raw = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
        mime_msg = email.message_from_bytes(msg_raw)
        return mime_msg

    except Exception as error:
        print(f'An error occurred: {error}')
        return None
    
def authenticate():
    creds = None
    print("authenticating")
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        print("already authenticated")
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            print("refreshing authentication")
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            print("refreshing authentication")
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def get_processed_message_ids(sheets_service, spreadsheet_id):
    try:
        result = (
            sheets_service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range="Sheet2!A:A")
            .execute()
        )
        
        values = []
        
        for row in result.get("values", []) :
            values.append(row[0])
            
        print(f"{len(values)} rows retrieved {values}")
        return values
    except HTTPError as error:
        print(f"An error occurred: {error}")
        return []