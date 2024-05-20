from .client import Client
import threading

thread_local = threading.local()

def get_client():
    if not hasattr(thread_local, 'client'):
        thread_local.client = Client()
    return thread_local.client

def configure(preimage_provider=None, credentials_service=None):
    get_client()._configure(preimage_provider, credentials_service)

def get(url, **kwargs):
    client = get_client()
    return client.request('GET', url, **kwargs)

def post(url, **kwargs):
    client = get_client()
    return client.request('POST', url, **kwargs)

def put(url, **kwargs):
    client = get_client()
    return client.request('PUT', url, **kwargs)

def delete(url, **kwargs):
    client = get_client()
    return client.request('DELETE', url, **kwargs)


class AsyncClient:
    def __init__(self, preimage_provider=None, credentials_service=None):
        self._client = get_client()
        
        if preimage_provider and credentials_service:
            self._client = Client(preimage_provider, credentials_service)

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
