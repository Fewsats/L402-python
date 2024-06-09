import httpx

from .client import Client
from .preimage_provider import PreimageProvider
from .credentials import CredentialsService, parse_http_402_response

_default_preimage_provider = None
_default_credentials_service = None

def configure(preimage_provider: PreimageProvider, credentials_service: CredentialsService):
    global _default_preimage_provider
    global _default_credentials_service

    _default_preimage_provider = preimage_provider
    _default_credentials_service = credentials_service
    
class AsyncClient(httpx.AsyncClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if _default_preimage_provider is None or _default_credentials_service is None:
            raise Exception("You must configure the client before using it.")
        
        self._preimage_provider = _default_preimage_provider
        self._credentials_service = _default_credentials_service
    
    def _add_authorization_header(self, request, credentials):
        """Adds the L402 Authorization header to the request."""
        request.headers['Authorization'] = credentials.authentication_header()

    async def _handle_402_payment_required(self, url: str, response: httpx.Response) -> CredentialsService:
        """Handles a 402 Payment Required response."""
        creds = parse_http_402_response(response)
        creds.set_location(url)
        preimage = await self._preimage_provider.get_preimage(creds.invoice)
        if not preimage:
            raise Exception("Payment failed.")

        creds.preimage = preimage
        await self._credentials_service.store(creds)

        return creds
    
    async def send(self, request, *args, **kwargs):
        url = str(request.url)
        creds = await self._credentials_service.get(url)
        if creds:
            self._add_authorization_header(request, creds)

        response = await super().send(request, *args, **kwargs)
        if response.status_code != 402:
            return response

        new_creds = await self._handle_402_payment_required(url, response)
        self._add_authorization_header(request, new_creds)
        return await super().send(request, *args, **kwargs)
    
