from dateutil import parser
import re

def create_details_object() :
    return {
        'message_id': None,
        'bank_name': None,
        'transaction_amount': None,
        'merchant': None,
        'date_time': None,
        'type': "debit"
    }

def extract_hdfc_transaction_details(email_content):
    details = create_details_object()
    details['bank_name'] = 'HDFC Bank'
    
    amount_pattern = r"Rs (\d+.\d+)"
    amount_match = re.search(amount_pattern, email_content)
    if amount_match:
        details['transaction_amount'] = amount_match.group(1)

    merchant_pattern = r"at (.*?) on"
    merchant_match = re.search(merchant_pattern, email_content)
    if merchant_match:
        details['merchant'] = merchant_match.group(1)

    return details

def extract_kotak_transaction_details(email_content):
    details = create_details_object()
    details['bank_name'] =  'Kotak Mahindra Bank Ltd'

    amount_pattern = r"A Transaction of INR (\d+.\d+)"
    amount_match = re.search(amount_pattern, email_content)
    if amount_match:
        details['transaction_amount'] = amount_match.group(1)

    merchant_pattern = r"at (.+?) on"
    merchant_match = re.search(merchant_pattern, email_content)
    if merchant_match:
        details['merchant'] = merchant_match.group(1)

    return details

def extract_citibank_transaction_details(email_content):
    details = create_details_object()
    details['bank_name'] =  'Citibank'

    amount_pattern = r"Rs\. (\d+(\.\d+)?)"
    amount_match = re.search(amount_pattern, email_content)
    if amount_match:
        details['transaction_amount'] = amount_match.group(1)

    merchant_pattern = r"at ([\w\s\-]+) on"
    merchant_match = re.search(merchant_pattern, email_content)
    if merchant_match:
        details['merchant'] = merchant_match.group(1).strip()

    return details

def extract_citibank_upi_transaction_details(email_content):
    details = create_details_object()
    details['bank_name'] =  'Citibank'

    amount_pattern = r"Rs\. (\d+(\.\d+)?)"
    amount_match = re.search(amount_pattern, email_content)
    if amount_match:
        details['transaction_amount'] = amount_match.group(1)

    merchant_pattern = r"at ([\w\s\-]+) on"
    merchant_match = re.search(merchant_pattern, email_content)
    if merchant_match:
        details['merchant'] = merchant_match.group(1).strip()

    return details

import re

def extract_citibank_upi_transaction_details_v2(email_content):
    details = create_details_object()
    details['bank_name'] =  'Citibank'

    if "Your Citibank A/c has been credited" in email_content:
        details['type'] = 'credit'
        merchant_pattern = r"received from (.*?). UPI"
        merchant_match = re.search(merchant_pattern, email_content)
        if merchant_match:
            details['merchant'] = merchant_match.group(1).strip()
    elif "Your Citibank A/c has been debited" in email_content:
        details['type'] = 'debit'
        merchant_pattern = r"and account (.*?) has been credited"
        merchant_match = re.search(merchant_pattern, email_content)
        if merchant_match:
            details['merchant'] = merchant_match.group(1).strip()

    amount_pattern = r"INR (\d+(?:\.\d{1,2})?)"
    amount_match = re.search(amount_pattern, email_content)
    if amount_match:
        details['transaction_amount'] = amount_match.group(1)

    return details

def get_header(header_name, headers):
    for name, value in headers:
        if name.lower() == header_name.lower():
            return value
    return None

def format_date(date_string):
    try:
        date_string = re.sub(r'\s*\([^)]*\)', '', date_string)
        parsed_date = parser.parse(date_string)
        return parsed_date.strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        # Handle the exception if parsing fails
        print(f"Failed to parse date: {date_string}")
        return ""