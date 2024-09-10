import pytest
import requests
from l402.client.requests import SyncClient, Session
from l402.client.credentials import L402Credentials

# Constants
TEST_MACAROON = "AgELZmV3c2F0cy5jb20CQgAAIHP9p+tLogUGNL0tgYsllbz3830vlSCc8urox4tIJgmyjCg6CeqRv5DMI0hfiZDI93gDGFci27ePiHda6UYAfAACH2V4cGlyZXNfYXQ9MjAyNC0xMC0xMFQxNDo1MToyNVoAAjBleHRlcm5hbF9pZD01MWJlMjlhZi1jMjQzLTQ4MDctOWM5Ni1hNjk3YTEwZTNkYWQAAAYgAcdSlT10N+ivLreBf+kfHnEeuXdatvg8E3NqUjZ8iMk="
TEST_INVOICE = "lnbc180n1pnwqh8dpp5ypelmfltfw3q2p35h5kcrze9jk700uma972jp88jat5v0z6gycysdpjf35kw6r5de5kueeqfejhgam0wf4jq5m5v968xgz8wfshq6z3fscqzzsxqyz5vqsp5fegk5cufyvdemwtg3vfqdyemnkkea6mgldvhlhu40hkpldq0dctq9qxpqysgq28scr3zum80jhqawtrh3tyzqz32jerxprujvamvfgnj2l4yhz8dq2m7f79w977f2l6z4mchxjck005n3x9vwzec6r5fmgmz2lafw00sqv6thxh"
TEST_PREIMAGE = "mock_preimage"
TEST_URL = "https://api.example.fewsats.com/v0/gateway/access/51be29af-c243-4807-9c96-a697a10e3dad"
TEST_AUTH_HEADER = "Bearer token"

@pytest.fixture
def mock_preimage_provider(mocker):
    provider = mocker.Mock()
    provider.get_preimage.return_value = TEST_PREIMAGE
    return provider

@pytest.fixture
def credentials_service(mocker):
    return mocker.Mock()

@pytest.fixture
def client(mock_preimage_provider, credentials_service):
    return SyncClient(mock_preimage_provider, credentials_service)

@pytest.fixture
def mock_response():
    response = requests.Response()
    response.status_code = 402
    response.headers['WWW-Authenticate'] = f'L402 macaroon="{TEST_MACAROON}", invoice="{TEST_INVOICE}"'
    return response

@pytest.fixture
def mock_session(mocker):
    session_mock = mocker.Mock(spec=requests.Session)
    session_mock.__enter__ = mocker.Mock(return_value=session_mock)
    session_mock.__exit__ = mocker.Mock(return_value=None)
    return session_mock

def test_add_authorization_header(client):
    kwargs = {}
    credentials = L402Credentials(TEST_MACAROON, TEST_PREIMAGE, TEST_INVOICE)
    credentials.authentication_header = lambda: TEST_AUTH_HEADER
    
    client._add_authorization_header(kwargs, credentials)
    
    assert kwargs["headers"]["Authorization"] == TEST_AUTH_HEADER

def test_handle_402_payment_required_success(client, mock_response):
    result = client._handle_402_payment_required(TEST_URL, mock_response)
    
    assert isinstance(result, L402Credentials)
    assert result.macaroon == TEST_MACAROON
    assert result.invoice == TEST_INVOICE
    assert result.preimage == TEST_PREIMAGE
    assert result.location == TEST_URL
    
    client.preimage_provider.get_preimage.assert_called_once_with(TEST_INVOICE)
    client.credentials_service.store.assert_called_once_with(result)

def test_handle_402_payment_required_failure(client, mock_response):
    client.preimage_provider.get_preimage.return_value = None

    with pytest.raises(Exception, match="Payment failed."):
        client._handle_402_payment_required(TEST_URL, mock_response)
    
    client.preimage_provider.get_preimage.assert_called_once()

def test_request_with_existing_creds(client, mocker, mock_session):
    url = "http://example.com"
    method = "GET"
    kwargs = {"data": {"key": "value"}}
    
    creds = L402Credentials(TEST_MACAROON, TEST_PREIMAGE, TEST_INVOICE)
    client.credentials_service.get.return_value = creds
    
    response = requests.Response()
    response.status_code = 200
    response._content = b'{"success": true}'
    
    mock_session.request.return_value = response
    mocker.patch("requests.Session", return_value=mock_session)
    
    result = client.request(method, url, **kwargs)
    
    assert result.status_code == 200
    assert result.json() == {"success": True}
    client.credentials_service.get.assert_called_once_with(url)
    
    # Check that request was called with correct arguments, including the Authorization header
    expected_kwargs = {
        "data": {"key": "value"},
        "headers": {"Authorization": f"L402 {TEST_MACAROON}:{TEST_PREIMAGE}"}
    }
    mock_session.request.assert_called_once_with(method, url, **expected_kwargs)

def test_request_with_402_handling(client, mocker, mock_response, mock_session):
    url = "http://example.com"
    method = "GET"
    kwargs = {"data": {"key": "value"}}
    
    client.credentials_service.get.return_value = None
    
    response_200 = requests.Response()
    response_200.status_code = 200
    response_200._content = b'{"success": true}'
    
    mock_session.request.side_effect = [mock_response, response_200]
    mocker.patch("requests.Session", return_value=mock_session)
    
    result = client.request(method, url, **kwargs)
    
    assert result.status_code == 200
    assert result.json() == {"success": True}
    client.credentials_service.get.assert_called_once_with(url)
    client.preimage_provider.get_preimage.assert_called_once()
    client.credentials_service.store.assert_called_once()
    assert mock_session.request.call_count == 2

class TestSession:
    @pytest.fixture
    def session(self):
        Session._instance = None
        Session._client = None
        Session._configured = False
        return Session()

    def test_singleton(self, session):
        assert session is Session()

    def test_is_configured(self, session, mock_preimage_provider, credentials_service):
        assert not session.is_configured
        session.configure(mock_preimage_provider, credentials_service)
        assert session.is_configured

    def test_configure(self, session, mock_preimage_provider, credentials_service):
        session.configure(mock_preimage_provider, credentials_service)
        assert isinstance(session._client, SyncClient)
        assert session.is_configured

    def test_request_not_configured(self, session):
        with pytest.raises(Exception, match="No request client configured."):
            session.request("GET", "http://example.com")

    def test_request_configured(self, session, mock_preimage_provider, credentials_service, mocker):
        session.configure(mock_preimage_provider, credentials_service)
        mock_response = mocker.Mock(spec=requests.Response)
        mocker.patch.object(session._client, "request", return_value=mock_response)
        
        response = session.request("GET", "http://example.com")
        
        assert response == mock_response
        session._client.request.assert_called_once_with("GET", "http://example.com")

    @pytest.mark.parametrize("method", ["get", "post", "put", "delete"])
    def test_http_methods(self, session, mock_preimage_provider, credentials_service, mocker, method):
        session.configure(mock_preimage_provider, credentials_service)
        mock_response = mocker.Mock(spec=requests.Response)
        mocker.patch.object(session, "request", return_value=mock_response)
        
        response = getattr(session, method)("http://example.com", data={"key": "value"})
        
        assert response == mock_response
        session.request.assert_called_once_with(method.upper(), "http://example.com", data={"key": "value"})

