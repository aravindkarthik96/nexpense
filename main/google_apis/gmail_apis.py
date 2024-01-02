import base64
import email
from requests import HTTPError
from googleapiclient.discovery import build

def get_email_serivce(creds) :
    return build('gmail', 'v1', credentials=creds)

def get_mime_message(email_service, user_id, msg_id):
    try:
        message = email_service.users().messages().get(userId=user_id, id=msg_id, format='raw').execute()
        msg_raw = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
        mime_msg = email.message_from_bytes(msg_raw)
        return mime_msg

    except Exception as error:
        print(f'An error occurred: {error}')
        return None

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
            
        print(f"{len(values)} rows retrieved")
        return values
    except HTTPError as error:
        print(f"An error occurred: {error}")
        return []
    
def get_message_ids(email_service,user_id,email_count):
    results = email_service.users().messages().list(userId=user_id, maxResults=email_count).execute()
    return results.get('messages', [])