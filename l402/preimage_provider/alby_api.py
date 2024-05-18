import requests
import httpx
import json

from .preimage_provider import PreimageProvider

class AlbyAPI(PreimageProvider):
    def __init__(self, api_key):
        self.api_key = api_key
        self.alby_url = "https://api.getalby.com"
    
    def _prepare_request(self, invoice: str) -> (str, dict, str):
        url = f"{self.alby_url}/payments/bolt11"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        data = json.dumps({"invoice": invoice})
        return url, headers, data
    
    def _process_response(self, response):
        if response.status_code != 200:
            raise Exception(f"Unexpected response ({response.status_code}): {response.text}")

        try:
            payment_response = response.json()
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON response: {response.text}")

        preimage = payment_response.get("payment_preimage")
        if not preimage:
            raise Exception(f"Payment preimage not found in response: {payment_response}")

        return preimage
    
    def get_preimage(self, invoice: str) -> str:
        url, headers, data = self._prepare_request(invoice)
        response = requests.post(url, headers=headers, data=data)
        return self._process_response(response)
    
    async def get_preimage_async(self, invoice: str) -> str:
        url, headers, data = self._prepare_request(invoice)
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=data)
        return self._process_response(response)