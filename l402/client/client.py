import httpx
import asyncio

from l402.preimage_provider import PreimageProvider
from l402.credentials import CredentialsService, parse_http_402_response

class Client:
    """
    The Client class is a low level HTTP client implementation that handles HTTP requests 
    with 402 Payment Required responses.
    """
    def __init__(self, preimage_provider: PreimageProvider, credentials_service: CredentialsService):
        self.preimage_provider = preimage_provider
        self.credentials_service = credentials_service

    def _configure(self, preimage_provider=None, credentials_service=None):
        """
        Configures the client with the given services.
        """
        if preimage_provider:
            self.preimage_provider = preimage_provider
        if credentials_service:
            self.credentials_service = credentials_service

    def _add_authorization_header(self, kwargs, credentials):
        """
        Adds the L402 Authorization header to the request.
        """
        headers = kwargs.setdefault('headers', {})
        headers['Authorization'] = credentials.authentication_header()
    
    def is_valid(self):
        """
        Checks if the client is configured with a preimage provider and a credentials service.
        """
        return self.preimage_provider and self.credentials_service

    async def _handle_402_payment_required(self, url, response):
        """
        Handles a 402 Payment Required response.
        """
        creds = parse_http_402_response(response)
        creds.set_location(url)
        preimage = await self.preimage_provider.get_preimage_async(creds.invoice)
        if not preimage:
            raise Exception("Payment failed.")

        creds.preimage = preimage
        self.credentials_service.insert(creds)
        return creds
       
    async def _make_request(self, method, url, **kwargs):
        """
        Makes a request to the given URL with the given method and kwargs.
        """
        creds = self.credentials_service.get(url)
        if creds:
            self._add_authorization_header(kwargs, creds)

        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, **kwargs)

            if response.status_code != 402:
                return response
            
            newCreds = await self._handle_402_payment_required(url, response)
            self._add_authorization_header(kwargs, newCreds)
            return await client.request(method, url, **kwargs)
    
    async def async_request(self, method, url, **kwargs):
        """
        Makes a request to the given url with the given method and kwargs.

        If we already have credentials for the given url, we will use them to
        authenticate the request.

        If we don't have credentials, we will make a request to the url with 
        the given method/kwargs and handle 402 Payment Required responses if
        needed.
        """
        return await self._make_request(method, url, **kwargs)

    def request(self, method, url, **kwargs):
        """
        Synchronous version of async_request. This will run the coroutine
        to completion and return the result.
        """
        return asyncio.run(self.async_request(method, url, **kwargs))