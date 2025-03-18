#!/usr/bin/env python3
import requests
import time
import sys

API_KEY = "TDRLSEriXgEHJcQo214Bzg==Aw9LxINGtDUx3LKq"
API_URL = "https://api.api-ninjas.com/v1/quotes"
HEADERS = {"X-Api-Key": API_KEY}

def fetch_quote():
    response = requests.get(API_URL, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        if data and isinstance(data, list) and len(data) > 0:
            quote_data = data[0]
            return f"{quote_data.get('quote', '')} - {quote_data.get('author', 'Unknown')}"
        else:
            return "No quote data returned."
    else:
        return f"Error fetching quote: {response.status_code}"

def type_out(text, delay=0.05):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write("\n")

if __name__ == "__main__":
    quote = fetch_quote()
    type_out(quote)
