import requests
from payments.alby_wallet import AlbyWallet
from credentials.credentials import parse_l402_challenge
from credentials.sqlite_store import SQLiteStore
import os 


default_credentials_service = SQLiteStore()
default_preimage_provider = AlbyWallet(api_key=os.getenv("ALBY_TOKEN"))


class Client:
    def __init__(self, preimage_provider=None, credentials_service=None):
        self.preimage_provider = preimage_provider or default_preimage_provider
        self.credentials_service = credentials_service or default_credentials_service


    def _configure(self, payments_service=None, credentials_service=None):
        if payments_service:
            self.preimage_provider = payments_service
        if credentials_service:
            self.credentials_service = credentials_service

    def _add_authorization_header(self, kwargs, credentials):
        if 'headers' in kwargs:
            kwargs['headers']['Authorization'] = credentials.authentication_header()
        else:
            kwargs['headers'] = {'Authorization': credentials.authentication_header()}

    def request(self, method, url, **kwargs):
        creds = self.credentials_service.get_l402_credentials(url, method)

        if creds:
            self._add_authorization_header(kwargs, creds)

        response = requests.request(method, url, **kwargs)
        if response.status_code != 402:
            return response

        creds = parse_l402_challenge(response)

        preimage = self.preimage_provider.get_preimage(creds.invoice)
        if not preimage:
            raise Exception("Payment failed.")

        creds.preimage = preimage
        self.credentials_service.save_l402_credentials(url, method, creds)
        self._add_authorization_header(kwargs, creds)

        return requests.request(method, url, **kwargs)
