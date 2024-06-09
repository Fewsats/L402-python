from typing import Tuple, Dict

import httpx
import json

from .preimage_provider import PreimageProvider

class AlbyAPI(PreimageProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.alby_url = "https://api.getalby.com"

    async def get_preimage(self, invoice: str) -> str:
        """
        Retrieves the preimage for the given invoice.

        Args:
            invoice (str): The invoice for which to retrieve the preimage.

        Returns:
            str: The preimage associated with the invoice.
        
        Raises:
            Exception: If unable to obtain the preimage.
        """
        url, headers, data = self._prepare_request(invoice)
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, content=data)
            return self._process_response(response)

    def _prepare_request(self, invoice: str) -> Tuple[str, str, str]:
        """
        Prepares the request to the Alby API to retrieve the preimage for the given invoice.

        Args:
            invoice (str): The invoice for which to retrieve the preimage.

        Returns:
            Tuple[str, str, str]: The URL, headers, and data for the request.
        """
        url = f"{self.alby_url}/payments/bolt11"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        data = json.dumps({'invoice': invoice})
        return url, headers, data

    def _process_response(self, response: httpx.Response) -> str:
        """
        Processes the response from the Alby API to retrieve the preimage.
        
        Args:
            response (httpx.Response): The response from the Alby API.
            
        Returns:
            str: The preimage associated with the invoice.
                
        Raises:
            Exception: If the response status code is not 200.
            Exception: If the response is not valid JSON with a payment preimage.
        """
        if response.status_code != 200:
            raise Exception(f"Unexpected response {response.status_code}: {response.text}, headers: {response.headers}, request details: {response.request}")


        try:
            payment_response = response.json()
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON response: {response.text}")
        
        preimage = payment_response.get("payment_preimage")
        if not preimage:
            raise Exception(f"Payment preimage not found in response: {payment_response}")

        return preimage