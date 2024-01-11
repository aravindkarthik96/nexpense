from PyQt6.QtWidgets import QMainWindow, QPushButton, QProgressBar
import openai
from constants import EMAIL_COUNT, SHEET_ID, USER_ID
from main.google_apis.gmail_apis import get_email_serivce, get_message_ids
from main.google_apis.sheets_apis import get_sheets_serivce
from main.processors.email_processor import EmailProcessorThread
from main.google_apis.auth_apis import authenticate


class MainWindow(QMainWindow):
    creds = None

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Nexpense")
        self.setGeometry(50, 100, 400, 200)

        self.sync_button = QPushButton("Sync Emails", self)
        self.sync_button.setGeometry(50, 20, 300, 40)

        self.get_insights_button = QPushButton("Gather Insights", self)
        self.get_insights_button.setGeometry(50, 70, 300, 40)
        
        self.progress = QProgressBar(self)
        self.progress.setGeometry(50, 140, 300, 20)
        
        self.sync_button.clicked.connect(self.autenticate_and_fetch_emails)
        self.get_insights_button.clicked.connect(self.get_insights_from_data)

    def syncEmails(self):
        print("fetching emails")
        email_service = get_email_serivce(self.creds)
        sheets_service = get_sheets_serivce(self.creds)

        messages = get_message_ids(email_service, USER_ID, EMAIL_COUNT)

        if not messages:
            print("No messages found.")
            return

        self.progress.setMaximum(len(messages))
        self.progress.setValue(0)
        self.sync_button.setDisabled(True)

        self.thread = EmailProcessorThread(email_service, sheets_service, messages)
        self.thread.update_progress.connect(self.update_progress)
        self.thread.finished.connect(self.fetching_complete)
        self.thread.start()

    def update_progress(self, value):
        self.progress.setValue(value)

    def fetching_complete(self):
        print(f"Completed syncing {EMAIL_COUNT} emails")
        self.sync_button.setDisabled(False)

    def autenticate_and_fetch_emails(self):
        self.creds = authenticate()
        self.syncEmails()

    def fetch_processed_transactions(self) -> str:
        service = get_sheets_serivce(creds=self.creds)

        sheet = service.spreadsheets()
        result = (
            sheet.values().get(spreadsheetId=SHEET_ID, range="Sheet1!A2:F").execute()
        )
        values = result.get("values", [])
        
        if len(values) > 100 :
            values = values[-100:]
        
        data = "dt,bnk,amt,typ,mrch"
        
        if not values:
            print("No data found.")
        else:
            for row in values:
                data = data + f";{row[1]},{row[2]},{row[3]},{row[4]},{row[5]}"
        # print(data)
        return data

    def get_insights_from_data(self):
        self.creds = authenticate()
        processed_transactions = self.fetch_processed_transactions()
        print(self.fetch_insights_from_gpt(processed_transactions))
    
    def fetch_insights_from_gpt(self, processed_transactions : str):
        prompt = f"Analyze this spending data and provide insights: {processed_transactions}, the data is a CSV of Date, Bank, Amount, Type, Merchant, I want you to share a very concise bullet points about the data I have shared, eg. monthly spends, weekly spends etc and anything else that's interesting you can offer. I also want you to share stuff like transaction breakdown per bank, merchant etc. do not share any extra stuff, act like you are an app that simply exists to give insights on the data and you are not directly talking to a person, just simply generating insights, I need the insights to be actual numbers totals etc, do not say stuff like  'Fewer transactions' 'moderate diversity in merchant types' etc, be mathematical and statistical , present the insights in the form of a table(ascii table) that's easy to read. Do not respond with anything other than the table"
        client = openai.OpenAI()
        
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt},]
        )
        
        return response.choices[0].message.content
