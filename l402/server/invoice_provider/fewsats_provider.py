import os
import httpx
import json
from typing import Tuple
from .invoice_provider import InvoiceProvider

class FewsatsInvoiceProvider(InvoiceProvider):
    """Concrete implementation of InvoiceProvider using the Fewsats API."""

    def __init__(self, base_url: str = "https://api.fewsats.com", api_key: str = ""):
        """Initialize the FewsatsInvoiceProvider.

        Args:
            base_url (str): The base URL of the Fewsats API. Defaults to "https://api.fewsats.com".
        """
        self.base_url = base_url
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = os.environ.get("FEWSATS_API_KEY")
        if not self.api_key:
            raise ValueError("Missing FEWSATS_API_KEY environment variable. Get one at https://fewsats.com/")

    def _prepare_request(self, amount: int, currency: str, description: str) -> Tuple[str, dict, str]:
        url = f"{self.base_url}/v0/invoices"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        data = json.dumps({
            "amount": amount,
            "currency": currency,
            "description": description
        })
        return url, headers, data

    def _process_response(self, response: httpx.Response) -> Tuple[str, str]:
        response.raise_for_status()

        try:
            invoice_data = response.json()
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON response: {response.text}")

        payment_request = invoice_data.get("PaymentRequest")
        payment_hash = invoice_data.get("PaymentHash")

        if not payment_request or not payment_hash:
            raise ValueError(f"Invalid response from Fewsats API: {invoice_data}")

        return payment_request, payment_hash

    async def create_invoice(self, amount: int, currency: str, description: str) -> Tuple[str, str]:
        """Create a new invoice using the Fewsats API.

        Args:
            amount (int): The amount of the invoice in the smallest unit of the currency (e.g., cents for USD).
            currency (str): The currency of the invoice (e.g., "USD").
            description (str): A brief description of the purpose of the invoice.

        Returns:
            Tuple[str, str]: A tuple containing the payment_request and payment_hash of the invoice.

        Raises:
            ValueError: If the API request fails or returns an unexpected response.
        """
        url, headers, data = self._prepare_request(amount, currency, description)
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, content=data)
            return self._process_response(response)
