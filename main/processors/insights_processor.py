import openai
from PyQt6.QtCore import QThread, pyqtSignal
from constants import SHEET_ID

from main.google_apis.sheets_apis import fetch_processed_transactions, get_sheets_serivce


class InsightsProcessorThread(QThread):
    update_progress = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, creds):
        super().__init__()
        self.creds = creds

    def run(self):
        transactions = fetch_processed_transactions(self.creds, SHEET_ID)
        transactions_string = self.get_transactions_as_string(transactions)
        print(self.fetch_insights_from_gpt(transactions_string))
        self.finished.emit()

    def get_transactions_as_string(self, transactions: list) -> str:
        if len(transactions) > 100:
            transactions = transactions[-100:]

        data = "dt,bnk,amt,typ,mrch"

        if not transactions:
            print("No data found.")
            self.update_progress.emit(1)
        else:
            transactions_count = len(transactions)
            for index, row in enumerate(transactions):
                self.update_progress.emit((index / transactions_count)*100)
                data = data + f";{row[1]},{row[2]},{row[3]},{row[4]},{row[5]}"
        return data

    def fetch_insights_from_gpt(self, processed_transactions: str):
        prompt = f"Analyze this spending data and provide insights: {processed_transactions}, the data is a CSV of Date, Bank, Amount(INR), Type, Merchant, I want you to share a very concise bullet points about the data I have shared, eg. monthly spends, weekly spends etc and anything else that's interesting you can offer. I also want you to share stuff like transaction breakdown per bank, merchant etc. do not share any extra stuff, act like you are an app that simply exists to give insights on the data and you are not directly talking to a person, just simply generating insights, I need the insights to beactual numbers totals etc, do not say stuff like  'Fewer transactions' 'moderate diversity in merchant types' etc, be mathematical and statistical, do not respond with anything other than"

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt},
            ],
        )

        return response.choices[0].message.content
