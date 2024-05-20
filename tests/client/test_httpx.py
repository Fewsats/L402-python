import pytest
from unittest.mock import patch, MagicMock
from l402.client.httpx import AsyncClient, get

@pytest.mark.asyncio
async def test_async_client_thread_safety(mocker):
    preimage_provider=mocker.AsyncMock()
    credentials_service=mocker.Mock()


    # Create multiple AsyncClient instances
    client1 = AsyncClient()
    client2 = AsyncClient(preimage_provider, credentials_service)

    # Check if different Client instances are created
    assert client1._client is not client2._client

    # Configure client1
    client1._client._configure(preimage_provider="Provider1", credentials_service="Service1")

    # Check if client2's configuration remains unchanged (i.e., None)
    assert client2._client.preimage_provider == preimage_provider
    assert client2._client.credentials_service == credentials_service
    assert client1._client.preimage_provider == "Provider1"
    assert client1._client.credentials_service == "Service1"

def test_get():
    with patch('l402.client.httpx.get_client') as mock_get_client:
        mock_client = MagicMock()
        mock_client.request.return_value = "response"
        mock_get_client.return_value = mock_client

        response = get("http://example.com")
        mock_client.request.assert_called_once_with('GET', "http://example.com")
        assert response == "response"
        assert response == "response"