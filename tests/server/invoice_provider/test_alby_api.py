import pytest
import json
from unittest.mock import patch, MagicMock
from l402.server.invoice_provider import AlbyAPI

@pytest.fixture
def alby_api():
    api_key = "random_api_key"
    return AlbyAPI(api_key)

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_create_invoice_success(mock_post, alby_api):
    amount = 1000
    currency = "sats"
    description = "Test invoice"

    expected_response_body = {
        "amount": 1000,
        "currency": "sats",
        "description": "Test invoice",
        "payment_hash": "f21334bffdb84f5fb4baee9d9bd951c6ddb6127ff488e2d9933e35e89b7b7c33",
        "payment_request": "lnbc10u1p3qjf84pp5ygp6xaser0wd6jk2r05zl8j2xqth9t2nrdz32qum7rkvcfyp9nksdqqcqzpgxqrrsssp5v44d8gew6yva4hd8gywpgw4n7z3mlw58mmzqts8yzm8zzgfq8xwq9qyyssqsn9qrw9kx7y633xwt9e68wk3xgj4cuq45t0d4hj8a0mxqk5yq6p8l6kn40h69wfr25e0h3gud9qqe0f0uycpzvt5uxw7rnhe4jkwfqpw3qk4e",
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = expected_response_body
    mock_post.return_value = mock_response

    payment_request, payment_hash = await alby_api.create_invoice(amount, currency, description)
    assert payment_request == expected_response_body["payment_request"]
    assert payment_hash == expected_response_body["payment_hash"]

    mock_post.assert_called_once_with(
        f"{alby_api.alby_url}/invoices",
        headers={
            "Authorization": f"Bearer {alby_api.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        content='{"amount": 1000, "currency": "sats", "description": "Test invoice"}'
    )

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_create_invoice_unexpected_response(mock_post, alby_api):
    amount = 1000
    currency = "sats"
    description = "Test invoice"

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_post.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        await alby_api.create_invoice(amount, currency, description)

    assert "Unexpected response" in str(exc_info.value)

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_create_invoice_invalid_json_response(mock_post, alby_api):
    amount = 1000
    currency = "sats"
    description = "Test invoice"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "Invalid JSON"
    mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", doc="", pos=0)
    mock_post.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        await alby_api.create_invoice(amount, currency, description)

    assert "Invalid JSON response" in str(exc_info.value)

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_create_invoice_missing_payment_request_or_hash(mock_post, alby_api):
    amount = 1000
    currency = "sats"
    description = "Test invoice"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}
    mock_post.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        await alby_api.create_invoice(amount, currency, description)

    assert "No payment request or hash found in response" in str(exc_info.value)