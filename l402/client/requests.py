from .client import Client

_requests_client = Client(None, None)

def _check_request_client():
    return _requests_client.is_valid()

def configure(preimage_provider=None, credentials_service=None):
    _requests_client._configure(preimage_provider, credentials_service)

def get(url, **kwargs):
    _check_request_client()
    return _requests_client.request('GET', url, **kwargs)

def post(url, **kwargs):
    _check_request_client()
    return _requests_client.request('POST', url, **kwargs)

def put(url, **kwargs):
    _check_request_client()
    return _requests_client.request('PUT', url, **kwargs)

def delete(url, **kwargs):
    _check_request_client()
    return _requests_client.request('DELETE', url, **kwargs)


