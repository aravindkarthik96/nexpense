import re

def extract_hdfc_transaction_details(email_content):
    details = {
        'bank_name': 'HDFC Bank',  # Inferred from the email's context, as it's static in this case
        'transaction_amount': None,
        'merchant': None,
        'date_time': None,
        'type': "debit"  # Added field
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
        'date_time': None,
        'type': "debit"  # Added field
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
        'date_time': None,
        'type': "debit"  # Added field
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
        'date_time': None,
        'type': "debit"  # Added field
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

import re

def extract_citibank_upi_transaction_details_v2(email_content):
    details = {
        'bank_name': 'Citibank',  # Known from the context
        'transaction_amount': None,
        'merchant': None,
        'date_time': None,
        'type': None  # Added field
    }

    # Look for "credited" or "debited" in the email content to determine the transaction type
    if "has been credited" in email_content:
        details['type'] = 'credit'
    elif "has been debited" in email_content:
        details['type'] = 'debit'

    # Remaining pattern matching as before
    amount_pattern = r"INR (\d+(?:\.\d{1,2})?)"
    amount_match = re.search(amount_pattern, email_content)
    if amount_match:
        details['transaction_amount'] = amount_match.group(1)

    date_time_pattern = r"on (\d{2}-\w{3}-\d{2,4} at \d{2}:\d{2})"
    date_time_match = re.search(date_time_pattern, email_content)
    if date_time_match:
        details['date_time'] = date_time_match.group(1)

    merchant_pattern = r"and account (.*?) has been credited"
    merchant_match = re.search(merchant_pattern, email_content)
    if merchant_match:
        details['merchant'] = merchant_match.group(1).strip()

    return details

def get_header(header_name, headers):
    """
    Fetches the header value for a given header name from a list of (Header, Value) tuples.
    """
    for name, value in headers:
        if name.lower() == header_name.lower():
            return value
    return None