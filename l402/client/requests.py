import requests
import asyncio
from l402.client import Client

from .exceptions import RequestException

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

    def configure(self, preimage_provider: str = None, credentials_service: str = None) -> None:
        """Configure the request client with given providers and services."""
        self._client = Client(preimage_provider, credentials_service)
        self._client.configure(preimage_provider, credentials_service)
        self._configured = True

    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Perform a request with optional parameters."""
        if not self.is_configured:
            raise RequestException("No request client configured.")
        return asyncio.run(self._client.request(method, url, **kwargs))

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


