from client.client import Client


_client = Client()

def configure(preimage_provider=None, credentials_service=None):
    _client._configure(preimage_provider, credentials_service)

def get(url, **kwargs):
    return _client.request('GET', url, **kwargs)

def post(url, **kwargs):
    return _client.request('POST', url, **kwargs)

def put(url, **kwargs):
    return _client.request('PUT', url, **kwargs)

def delete(url, **kwargs):
    return _client.request('DELETE', url, **kwargs)


