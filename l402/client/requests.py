import requests
from .exceptions import RequestException
from .preimage_provider import PreimageProvider
from .credentials import CredentialsService, parse_http_402_response, L402Credentials

class SyncClient:
    def __init__(self, preimage_provider: PreimageProvider = None, 
                 credentials_service: CredentialsService = None):
        self.preimage_provider = preimage_provider
        self.credentials_service = credentials_service
        
    def _add_authorization_header(self, kwargs, credentials):
        """Adds the L402 Authorization header to the request."""
        headers = kwargs.setdefault('headers', {})
        headers['Authorization'] = credentials.authentication_header()

    def _handle_402_payment_required(self, url: str, response: requests.Response) -> L402Credentials:
        """Handles a 402 Payment Required response."""
        creds = parse_http_402_response(response)
        creds.set_location(url)
        preimage = self.preimage_provider.get_preimage(creds.invoice)
        if not preimage:
            raise Exception("Payment failed.")

        creds.preimage = preimage
        self.credentials_service.store(creds)
        return creds

    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        creds = self.credentials_service.get(url)
        if creds:
            self._add_authorization_header(kwargs, creds)

        with requests.Session() as session:
            response = session.request(method, url, **kwargs)
            if response.status_code != 402:
                return response

            new_creds = self._handle_402_payment_required(url, response)
            self._add_authorization_header(kwargs, new_creds)
            return session.request(method, url, **kwargs)

class Session:
    _instance = None
    _client = None
    _configured = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Session, cls).__new__(cls)
        return cls._instance

    @property
    def is_configured(self) -> bool:
        """Check if the request client is configured."""
        return self._configured

    def configure(self, preimage_provider: PreimageProvider = None, credentials_service: CredentialsService = None) -> None:
        """Configure the request client with given providers and services."""
        self._client = SyncClient(preimage_provider, credentials_service)
        self._configured = True

    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Perform a request with optional parameters."""
        if not self.is_configured:
            raise RequestException("No request client configured.")
        return self._client.request(method, url, **kwargs)

    def get(self, url: str, **kwargs) -> requests.Response:
        """Perform a GET request with optional parameters."""
        return self.request('GET', url, **kwargs)

    def post(self, url: str, **kwargs) -> requests.Response:
        """Perform a POST request with optional parameters."""
        return self.request('POST', url, **kwargs)

    def put(self, url: str, **kwargs) -> requests.Response:
        """Perform a PUT request with optional parameters."""
        return self.request('PUT', url, **kwargs)

    def delete(self, url: str, **kwargs) -> requests.Response:
        """Perform a DELETE request with optional parameters."""
        return self.request('DELETE', url, **kwargs)


