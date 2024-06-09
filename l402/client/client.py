import httpx
import asyncio

from .preimage_provider import PreimageProvider
from .credentials import CredentialsService, parse_http_402_response

class Client:
    """
    The Client class is a low-level HTTP client implementation that handles HTTP requests 
    with 402 Payment Required responses.
    """

    def __init__(self, preimage_provider: PreimageProvider = None, 
                 credentials_service: CredentialsService = None):
        self._preimage_provider = preimage_provider
        self._credentials_service = credentials_service

        self._lock = asyncio.Lock()

    @property
    def preimage_provider(self) -> PreimageProvider:
        return self._preimage_provider

    @property
    def credentials_service(self) -> CredentialsService:
        return self._credentials_service

    def configure(self, preimage_provider: PreimageProvider = None, credentials_service: CredentialsService = None):
        """Configures the client with the given services."""
        if preimage_provider:
            self._preimage_provider = preimage_provider
        if credentials_service:
            self._credentials_service = credentials_service

    def _add_authorization_header(self, kwargs, credentials):
        """Adds the L402 Authorization header to the request."""
        headers = kwargs.setdefault('headers', {})
        headers['Authorization'] = credentials.authentication_header()

    async def _handle_402_payment_required(self, url: str, response: httpx.Response) -> CredentialsService:
        """Handles a 402 Payment Required response."""
        creds = parse_http_402_response(response)
        creds.set_location(url)
        preimage = await self.preimage_provider.get_preimage(creds.invoice)
        if not preimage:
            raise Exception("Payment failed.")

        creds.preimage = preimage
        await self.credentials_service.store(creds)
        return creds

    async def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        async with self._lock:
            creds = await self.credentials_service.get(url)
            if creds:
                self._add_authorization_header(kwargs, creds)

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.request(method, url, **kwargs)
                if response.status_code != 402:
                    return response

                new_creds = await self._handle_402_payment_required(url, response)
                self._add_authorization_header(kwargs, new_creds)
                return await client.request(method, url, **kwargs)
