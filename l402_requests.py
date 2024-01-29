import requests
from payments.alby_wallet import AlbyWallet
from credentials.memory import InMemoryStore
from credentials.credentials import parse_l402_challenge, decode_price
# from credentials import InMemoryStore, PersistentStore
import os 



class _L402Client:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(_L402Client, cls).__new__(cls)
            # Default services
            # TODO(with jordi): decide on final names for this
            cls._instance.payment_service = AlbyWallet(api_key=os.getenv("ALBY_TOKEN")) # PreimageProvider, PaymentProvider
            cls._instance.credentials_service = InMemoryStore() # #CredentialsProvider, CredentialsStore? 
        return cls._instance

    def configure(self, payments_service=None, credentials_service=None):
        if payments_service:
            self.payment_service = payments_service
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
        # invoice_price = decode_price(creds.invoice)

        print(f"URL: {url}")
        # print(f"Lightning invoice price: {invoice_price} sats")
        # user_input = input("Do you want to continue? (y/N): ")
        # if user_input.lower() != 'y':
        #     raise Exception("Payment declined by the user.")

        preimage = self.payment_service.get_preimage(creds.invoice)
        if not preimage:
            raise Exception("Payment failed.")

        creds.preimage = preimage
        self.credentials_service.save_l402_credentials(url, method, creds)
        self._add_authorization_header(kwargs, creds)

        return requests.request(method, url, **kwargs)

    def _decode_price(self, invoice):
        # Simplified decoding logic
        return int(invoice.split('amount=')[1].split('&')[0])

_client = _L402Client()

def configure(payment_service=None, credentials_service=None):
    _client.configure(payment_service, credentials_service)

def get(url, **kwargs):
    return _client.request('GET', url, **kwargs)

def post(url, **kwargs):
    return _client.request('POST', url, **kwargs)

def put(url, **kwargs):
    return _client.request('PUT', url, **kwargs)

def delete(url, **kwargs):
    return _client.request('DELETE', url, **kwargs)


if __name__ == "__main__":
    import l402_requests as l402_requests
    # from token_service import MemoryTokenStore

    # Configure the client to use a memory token store
    # requests.configure(token_service=MemoryTokenStore())

    # Now all requests will use the configured memory token store
    file_url = "https://api.staging.fewsats.com/v0/storage/download/2f8f1000-73fd-4578-8249-dd6949641e6a"

    response = l402_requests.get(file_url)
    print(response.text)

