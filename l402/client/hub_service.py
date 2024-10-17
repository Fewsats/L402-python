import requests
from typing import Optional
from urllib.parse import quote
import os
from .credentials import L402Credentials, CredentialsService
from .preimage_provider import PreimageProvider

class HubService(CredentialsService, PreimageProvider):
    def __init__(self, api_key: str = None, api_url: str = "https://hub-5n97k.ondigitalocean.app/", ignore_existing_credentials: bool = False):
        self.api_url = api_url
        self.api_key = api_key or os.environ.get("HUB_API_KEY")
        self.ignore_existing_credentials = ignore_existing_credentials
        if not self.api_key:
            raise ValueError("API key must be provided either as an argument or in the HUB_API_KEY environment variable")

    def store(self, credentials: L402Credentials):
        # The store method is left empty as it's filled by the purchase itself
        pass

    def get(self, location: str, ) -> Optional[L402Credentials]:
        if self.ignore_existing_credentials:
            return None

        headers = self._get_headers()
        encoded_location = quote(location)
        response = requests.get(
            f"{self.api_url}/v0/l402/purchases/by-url?l402_url={encoded_location}",
            headers=headers
        )
        
        if response.status_code == 404:
            return None
        elif response.status_code != 200:
            raise Exception(f"Failed to retrieve credentials: {response.text}")

        purchase = response.json()
        return L402Credentials(
            macaroon=purchase["macaroon"],
            preimage=purchase["preimage"],
            invoice=purchase["invoice"]
        )

    def get_preimage(self, invoice: str) -> str:
        headers = self._get_headers()
        data = {
            "invoice": invoice,
            "macaroon": "",
            "l402_url": "",
            "description": "Invoice payment for preimage retrieval"
        }

        response = requests.post(
            f"{self.api_url}/v0/l402/purchases/direct",
            json=data,
            headers=headers
        )

        if response.status_code != 200:
            raise Exception(f"Failed to pay invoice: {response.text}")

        purchase_data = response.json()
        preimage = purchase_data.get("preimage")

        if not preimage:
            raise Exception("Preimage not found in the response")

        return preimage

    def _get_headers(self):
        return {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json"
        }