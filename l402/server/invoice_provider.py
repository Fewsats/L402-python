# /server/invoice_provider.py

import requests
import json

class InvoiceProvider:
    def create_invoice(self, price, currency):
        """Create an invoice for the given price and currency."""
        raise NotImplementedError("This method should be overridden by subclasses.")

class AlbyInvoiceProvider(InvoiceProvider):
    def __init__(self, api_key):
        self.api_key = api_key
        self.supported_currencies = ["BTC", "USD"]
        self.url = "https://api.getalby.com/invoices"

    def supported_currency(self, currency):
        return currency in self.supported_currencies

    def create_invoice(self, price, currency, description=""):
        if not self.supported_currency(currency):
            raise ValueError(f"Currency {currency} not supported")

        data = {
            "amount": price,
            "currency": currency,
            "description": description
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        response = requests.post(self.url, headers=headers, json=data)
        if response.status_code != 200:
            raise Exception(f"Failed to create invoice: {response.text}")

        return response.json()
