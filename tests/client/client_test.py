import pytest
from httpx import Response
from l402.client import Client
from l402.credentials import L402Credentials

def test_add_authorization_header(mocker):
    client = Client(preimage_provider=None, credentials_service=None)
    
    credentials = mocker.MagicMock(spec=L402Credentials)
    credentials.authentication_header.return_value = "Bearer token"
    
    kwargs = {}
    client._add_authorization_header(kwargs, credentials)
    
    assert kwargs["headers"]["Authorization"] == "Bearer token"
    credentials.authentication_header.assert_called_once()

@pytest.mark.asyncio
async def test_handle_402_payment_required_success(mocker):
    client = Client(preimage_provider=mocker.AsyncMock(), credentials_service=mocker.Mock())

    url = "http://example.com"
    response = mocker.MagicMock(spec=Response)

    creds = mocker.MagicMock(spec=L402Credentials)
    creds.invoice = "lnbc...."

    mocker.patch("l402.client.client.parse_http_402_response", return_value=creds)

    preimage = "preimage"
    client.preimage_provider.get_preimage_async.return_value = preimage

    await client._handle_402_payment_required(url, response)

    client.preimage_provider.get_preimage_async.assert_awaited_once_with(creds.invoice)
    assert creds.preimage == preimage
    client.credentials_service.insert.assert_called_once_with(creds)

@pytest.mark.asyncio
async def test_handle_402_payment_required_failure(mocker):
    client = Client(preimage_provider=mocker.AsyncMock(), credentials_service=mocker.AsyncMock())

    url = "http://example.com"
    response = mocker.MagicMock(spec=Response)

    creds = mocker.MagicMock(spec=L402Credentials)
    creds.invoice = "invoice"

    mocker.patch("l402.client.client.parse_http_402_response", return_value=creds)

    client.preimage_provider.get_preimage_async.return_value = None  # Simulate payment failure

    with pytest.raises(Exception) as exc_info:
        await client._handle_402_payment_required(url, response)

    assert str(exc_info.value) == "Payment failed."

    client.preimage_provider.get_preimage_async.assert_awaited_once_with(creds.invoice)

@pytest.mark.asyncio
async def test_make_request_with_existing_creds(mocker):
    client = Client(preimage_provider=mocker.AsyncMock(), credentials_service=mocker.Mock())

    url = "http://example.com"
    method = "GET"
    kwargs = {"data": {"key": "value"}}

    creds = mocker.MagicMock(spec=L402Credentials)
    client.credentials_service.get.return_value = creds

    response_mock = mocker.MagicMock(spec=Response)
    response_mock.status_code = 200
    async_client_mock = mocker.AsyncMock()
    async_client_mock.__aenter__.return_value.request.return_value = response_mock
    mocker.patch("httpx.AsyncClient", return_value=async_client_mock)

    add_authorization_header_mock = mocker.patch.object(client, "_add_authorization_header")

    response = await client._make_request(method, url, **kwargs)

    assert response == response_mock
    client.credentials_service.get.assert_called_once_with(url)
    add_authorization_header_mock.assert_called_once_with(kwargs, creds)
    async_client_mock.__aenter__.return_value.request.assert_awaited_once_with(method, url, **kwargs)

@pytest.mark.asyncio
async def test_make_request_success_without_402(mocker):
    client = Client(preimage_provider=mocker.AsyncMock(), credentials_service=mocker.Mock())

    url = "http://example.com"
    method = "GET"
    kwargs = {"data": {"key": "value"}}

    client.credentials_service.get.return_value = None

    response_mock = mocker.MagicMock(spec=Response)
    response_mock.status_code = 200
    async_client_mock = mocker.AsyncMock()
    async_client_mock.__aenter__.return_value.request.return_value = response_mock
    mocker.patch("httpx.AsyncClient", return_value=async_client_mock)

    add_authorization_header_mock = mocker.patch.object(client, "_add_authorization_header")

    response = await client._make_request(method, url, **kwargs)

    assert response == response_mock
    client.credentials_service.get.assert_called_once_with(url)
    add_authorization_header_mock.assert_not_called()
    async_client_mock.__aenter__.return_value.request.assert_awaited_once_with(method, url, **kwargs)

@pytest.mark.asyncio
async def test_make_request_with_402_handling(mocker):
    client = Client(preimage_provider=mocker.AsyncMock(), credentials_service=mocker.Mock())

    url = "http://example.com"
    method = "GET"
    kwargs = {"data": {"key": "value"}}

    client.credentials_service.get.return_value = None

    response_mock_402 = mocker.MagicMock(spec=Response)
    response_mock_402.status_code = 402
    response_mock_200 = mocker.MagicMock(spec=Response)
    response_mock_200.status_code = 200
    async_client_mock = mocker.AsyncMock()
    async_client_mock.__aenter__.return_value.request.side_effect = [response_mock_402, response_mock_200]
    mocker.patch("httpx.AsyncClient", return_value=async_client_mock)

    creds = mocker.MagicMock(spec=L402Credentials)
    handle_402_payment_required_mock = mocker.patch.object(client, "_handle_402_payment_required", return_value=creds)
    add_authorization_header_mock = mocker.patch.object(client, "_add_authorization_header")

    response = await client._make_request(method, url, **kwargs)

    assert response == response_mock_200
    client.credentials_service.get.assert_called_once_with(url)
    handle_402_payment_required_mock.assert_awaited_once_with(url, response_mock_402)

    add_authorization_header_mock.assert_called_once_with(kwargs, creds)

    assert async_client_mock.__aenter__.return_value.request.await_count == 2
