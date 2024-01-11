from googleapiclient.discovery import build

def get_sheets_serivce(creds) :
    return build('sheets', 'v4', credentials= creds)


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
    values = []
    for transaction in transactions:
        try:
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

    result = sheets_service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range="Sheet1",
        valueInputOption="USER_ENTERED",
        body=body).execute()
    print(f"{result.get('updates').get('updatedCells')} cells appended.")

def set_header_row(previously_processed_emails, sheets_service, spreadsheet_id):
    if len(previously_processed_emails)>0:
        print("Header already exists")
        return
    
    print("Setting header row as 'MessageID | Date | Bank | Amount | Type | Merchant'")
    values = [["MessageID","Date","Bank", "Amount", "Type", "Merchant"]]

    body = {
        'values': values
    }


    result = sheets_service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range="Sheet1",
        valueInputOption="USER_ENTERED",
        body=body).execute()
    print(f"{result.get('updates').get('updatedCells')} cells appended.")
    
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

def fetch_processed_transactions(creds,spreadsheet_id) -> list:
        service = get_sheets_serivce(creds=creds)

        sheet = service.spreadsheets()
        result = (
            sheet.values().get(spreadsheetId=spreadsheet_id, range="Sheet1!A2:F").execute()
        )
        return result.get("values", [])