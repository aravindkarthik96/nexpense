from googleapiclient.discovery import build
from requests import HTTPError


def get_sheets_serivce(creds):
    return build("sheets", "v4", credentials=creds)


def upload_processed_message_ids(sheets_service, spreadsheet_id, message_ids):
    print(f"Uploading processed messages")
    values = []

    for message_id in message_ids:
        values.append([message_id])

    body = {"values": values}

    result = (
        sheets_service.spreadsheets()
        .values()
        .append(
            spreadsheetId=spreadsheet_id,
            range="Sheet2",
            valueInputOption="USER_ENTERED",
            body=body,
        )
        .execute()
    )
    print(f"{result.get('updates').get('updatedCells')} cells appended.")


def upload_transactions_to_sheet(sheets_service, spreadsheet_id, transactions):
    print(f"Uploading emails to sheets {len(transactions)}")
    values = []
    for transaction in transactions:
        try:
            transaction_json = transaction

            values.append(
                [
                    transaction_json["message_id"],
                    transaction_json["date_time"],
                    transaction_json["bank_name"],
                    transaction_json["transaction_amount"],
                    transaction_json["type"],
                    transaction_json["merchant"],
                ]
            )

        except Exception as error:
            print(f"Invalid JSON string - message: {transaction} error: {error}")
            return "Invalid JSON string"

    body = {"values": values}

    result = (
        sheets_service.spreadsheets()
        .values()
        .append(
            spreadsheetId=spreadsheet_id,
            range="Sheet1",
            valueInputOption="USER_ENTERED",
            body=body,
        )
        .execute()
    )
    print(f"{result.get('updates').get('updatedCells')} cells appended.")


def set_header_row(previously_processed_emails, sheets_service, spreadsheet_id):
    if len(previously_processed_emails) > 0:
        print("Header already exists")
        return

    print("Setting header row as 'MessageID | Date | Bank | Amount | Type | Merchant'")
    values = [["MessageID", "Date", "Bank", "Amount", "Type", "Merchant"]]

    body = {"values": values}

    result = (
        sheets_service.spreadsheets()
        .values()
        .append(
            spreadsheetId=spreadsheet_id,
            range="Sheet1",
            valueInputOption="USER_ENTERED",
            body=body,
        )
        .execute()
    )
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

        for row in result.get("values", []):
            values.append(row[0])

        print(f"{len(values)} rows retrieved")
        return values
    except HTTPError as error:
        print(f"An error occurred: {error}")
        return []


def fetch_processed_transactions(creds, spreadsheet_id) -> list:
    service = get_sheets_serivce(creds=creds)

    sheet = service.spreadsheets()
    result = (
        sheet.values().get(spreadsheetId=spreadsheet_id, range="Sheet1!A2:G").execute()
    )
    return result.get("values", [])

def set_tag_on_row(sheets_service, spreadsheet_id, row_number, new_tag):
    try:
        tag_range = f'Sheet1!G{row_number}'
        values = [[new_tag]]
        body = {'values': values}
        update_result = sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=tag_range,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()

        print(f"Tag updated at row {row_number}. {update_result.get('updatedCells')} cells updated.")

    except Exception as e:
        print(f"An error occurred: {e}")

def find_row_by_message_id_and_update_tag(sheets_service, spreadsheet_id, message_id, new_tag):
    try:
        column_range = 'Sheet1!A:A'
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=column_range
        ).execute()

        message_ids = result.get('values', [])

        row_number = next((i + 1 for i, val in enumerate(message_ids) if val and val[0] == message_id), None)

        if row_number is not None:
            tag_range = f'Sheet1!G{row_number}'
            values = [[new_tag]]
            body = {'values': values}
            update_result = sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=tag_range,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()

            print(f"Tag updated for message ID '{message_id}' at row {row_number}. {update_result.get('updatedCells')} cells updated.")
        else:
            print(f"Message ID '{message_id}' not found in the spreadsheet.")

    except Exception as e:
        print(f"An error occurred: {e}")

def fetch_tags(creds, spreadsheet_id) -> list:
    service = get_sheets_serivce(creds=creds)

    sheet = service.spreadsheets()
    result = (
        sheet.values().get(spreadsheetId=spreadsheet_id, range="tags!A:A").execute()
    )
    
    tags = [row[0] for row in result.get("values", []) if row]
    
    return tags

def upload_new_tag(sheets_service, spreadsheet_id, new_tag):
    print(f"Uploading new tag")
    body = {"values": [[new_tag]]}

    result = (
        sheets_service.spreadsheets()
        .values()
        .append(
            spreadsheetId=spreadsheet_id,
            range="tags",
            valueInputOption="USER_ENTERED",
            body=body,
        )
        .execute()
    )
    print(f"{result.get('updates').get('updatedCells')} cells appended.")

