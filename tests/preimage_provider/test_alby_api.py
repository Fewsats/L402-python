import json
import pytest
from unittest.mock import patch, Mock

from l402.preimage_provider import AlbyAPI

example_response_body = {
    "amount": 100,
    "description": "Alby invoice",
    "destination": "025c1d5d1b4c983cc6350fc2d756fbb59b4dc365e45e87f8e3afe07e24013e8220",
    "fee": 0,
    "payment_hash": "38caadbe0f6112d9b638e9ae24338f7e9bd930a3387100da776644e56965c9c1",
    "payment_preimage": "2f84e22556af9919f695d7761f404e98ff98058b7d32074de8c0c83bf63eecd7",
    "payment_request": "lnbcrt1u1p3d23dkpp58r92m0s0vyfdnd3caxhzgvu006dajv9r8pcspknhvezw26t9e8qsdq5g9kxy7fqd9h8vmmfvdjscqzpgxqyz5vqsp59efe44rg6cjl3xwh9glgx4ztcgwtg5l8uhry2v9v7s0zn2wpaz2s9qyyssq2z799an4pt4wtfy8yrk5ee0qqj7w5a74prz5tm8rulwez08ttlaz9xx7eqw7fe94y7t0600d03k55fyguyj24nd9tjmx6sf7dsxkk4gpkyenl8"
}

@pytest.fixture
def alby_api():
    api_key = "your_api_key"
    return AlbyAPI(api_key)

@patch("requests.post")
def test_get_preimage_success(mock_post, alby_api):
    invoice = "your_invoice"
    expected_response_body = {
        "amount": 100,
        "description": "Alby invoice",
        "destination": "025c1d5d1b4c983cc6350fc2d756fbb59b4dc365e45e87f8e3afe07e24013e8220",
        "fee": 0,
        "payment_hash": "38caadbe0f6112d9b638e9ae24338f7e9bd930a3387100da776644e56965c9c1",
        "payment_preimage": "2f84e22556af9919f695d7761f404e98ff98058b7d32074de8c0c83bf63eecd7",
        "payment_request": "lnbcrt1u1p3d23dkpp58r92m0s0vyfdnd3caxhzgvu006dajv9r8pcspknhvezw26t9e8qsdq5g9kxy7fqd9h8vmmfvdjscqzpgxqyz5vqsp59efe44rg6cjl3xwh9glgx4ztcgwtg5l8uhry2v9v7s0zn2wpaz2s9qyyssq2z799an4pt4wtfy8yrk5ee0qqj7w5a74prz5tm8rulwez08ttlaz9xx7eqw7fe94y7t0600d03k55fyguyj24nd9tjmx6sf7dsxkk4gpkyenl8"
    }
    expected_preimage = "2f84e22556af9919f695d7761f404e98ff98058b7d32074de8c0c83bf63eecd7"

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = expected_response_body
    mock_post.return_value = mock_response

    preimage = alby_api.get_preimage(invoice)
    assert preimage == expected_preimage

    mock_post.assert_called_once_with(
        f"{alby_api.alby_url}/payments/bolt11",
        headers={
            "Authorization": f"Bearer {alby_api.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        data=json.dumps({"invoice": invoice})
    )

@patch("requests.post")
def test_get_preimage_missing_preimage(mock_post, alby_api):
    invoice = "your_invoice"
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}
    mock_post.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        alby_api.get_preimage(invoice)

    assert str(exc_info.value) == "Payment preimage not found in response: {}"

@patch("requests.post")
def test_get_preimage_unexpected_response(mock_post, alby_api):
    invoice = "your_invoice"
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_post.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        alby_api.get_preimage(invoice)

    assert str(exc_info.value) == "Unexpected response (500): Internal Server Error"


@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_get_preimage_async_success(mock_post, alby_api):
    invoice = "your_invoice"
    expected_response_body = {
        "amount": 100,
        "description": "Alby invoice",
        "destination": "025c1d5d1b4c983cc6350fc2d756fbb59b4dc365e45e87f8e3afe07e24013e8220",
        "fee": 0,
        "payment_hash": "38caadbe0f6112d9b638e9ae24338f7e9bd930a3387100da776644e56965c9c1",
        "payment_preimage": "2f84e22556af9919f695d7761f404e98ff98058b7d32074de8c0c83bf63eecd7",
        "payment_request": "lnbcrt1u1p3d23dkpp58r92m0s0vyfdnd3caxhzgvu006dajv9r8pcspknhvezw26t9e8qsdq5g9kxy7fqd9h8vmmfvdjscqzpgxqyz5vqsp59efe44rg6cjl3xwh9glgx4ztcgwtg5l8uhry2v9v7s0zn2wpaz2s9qyyssq2z799an4pt4wtfy8yrk5ee0qqj7w5a74prz5tm8rulwez08ttlaz9xx7eqw7fe94y7t0600d03k55fyguyj24nd9tjmx6sf7dsxkk4gpkyenl8"
    }
    expected_preimage = "2f84e22556af9919f695d7761f404e98ff98058b7d32074de8c0c83bf63eecd7"

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = expected_response_body
    mock_post.return_value = mock_response

    preimage = await alby_api.get_preimage_async(invoice)

    assert preimage == expected_preimage
    mock_post.assert_called_once_with(
        f"{alby_api.alby_url}/payments/bolt11",
        headers={
            "Authorization": f"Bearer {alby_api.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        data=json.dumps({"invoice": invoice})
    )


@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_get_preimage_async_unexpected_response(mock_post, alby_api):
    invoice = "your_invoice"
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_post.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        await alby_api.get_preimage_async(invoice)

    assert str(exc_info.value) == "Unexpected response (500): Internal Server Error"

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_get_preimage_async_missing_preimage(mock_post, alby_api):
    invoice = "your_invoice"
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}
    mock_post.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        await alby_api.get_preimage_async(invoice)

    assert str(exc_info.value) == "Payment preimage not found in response: {}"
