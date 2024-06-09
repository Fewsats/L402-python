import httpx
import json
from typing import Tuple

from .invoice_provider import InvoiceProvider

class AlbyAPI(InvoiceProvider):
    def __init__(self, api_key):
        self.api_key = api_key
        self.alby_url = "https://api.getalby.com"
    
    def _prepare_request(self, amount: int, currency: str, description: str) -> Tuple[str, str]:
        url = f"{self.alby_url}/invoices"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        data = json.dumps({
            "amount": amount, 
            "currency": currency,
            "description": description,
        })
        return url, headers, data
    
    def _process_response(self, response):
        if response.status_code != 200:
            raise Exception(f"Unexpected response ({response.status_code}): {response.text}")

        try:
            new_invoice_response = response.json()
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON response: {response.text}")
        
        payment_request = new_invoice_response.get("payment_request")
        payment_hash = new_invoice_response.get("payment_hash")

        if not payment_request or not payment_hash:
            raise Exception(f"No payment request or hash found in response: {new_invoice_response}")
        
        return payment_request, payment_hash
    
    async def create_invoice(self, amount: int, currency: str, description: str) -> Tuple[str, str]:
        url, headers, data = self._prepare_request(amount, currency, description)
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, content=data)
            return self._process_response(response)
    