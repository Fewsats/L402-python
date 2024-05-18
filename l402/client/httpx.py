from .client import Client

_httpx_client = Client(None, None)

def _check_httpx_client():
    return _httpx_client.is_valid()

def configure(preimage_provider=None, credentials_service=None):
    _httpx_client._configure(preimage_provider, credentials_service)

def get(url, **kwargs):
    _check_httpx_client()
    return _httpx_client.request('GET', url, **kwargs)

def post(url, **kwargs):
    _check_httpx_client()
    return _httpx_client.request('POST', url, **kwargs)

def put(url, **kwargs):
    _check_httpx_client()
    return _httpx_client.request('PUT', url, **kwargs)

def delete(url, **kwargs):
    _check_httpx_client()
    return _httpx_client.request('DELETE', url, **kwargs)


class AsyncClient:
    def __init__(self):
        # TODO(positiveblue): pass the constructor parameters to create 
        # an instance of the client that is thread-safe.
        self._client = _httpx_client

    async def __aenter__(self):
        if not self._client.is_valid():
            self._client._configure()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Clean up resources here, if necessary
        pass

    async def get(self, url, **kwargs):
        return await self._client.async_request('GET', url, **kwargs)

    async def post(self, url, **kwargs):
        return await self._client.async_request('POST', url, **kwargs)

    async def put(self, url, **kwargs):
        return await self._client.async_request('PUT', url, **kwargs)

    async def delete(self, url, **kwargs):
        return await self._client.async_request('DELETE', url, **kwargs)