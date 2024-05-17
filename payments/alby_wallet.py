import requests
import json

class AlbyWallet:
    def __init__(self, api_key):
        self.api_key = api_key
        self.alby_url = "https://api.getalby.com"

    def get_preimage(self, invoice):
        url = f"{self.alby_url}/payments/bolt11"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        data = json.dumps({"invoice": invoice})
        
        response = requests.post(url, headers=headers, data=data)
        
        if response.status_code != 200:
            raise Exception(f"Unexpected response ({response.status_code}): {response.text}")
        
        payment_response = response.json()
        return payment_response.get("payment_preimage")
