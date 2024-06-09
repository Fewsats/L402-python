import pytest
import os
from unittest.mock import AsyncMock, MagicMock

from pymacaroons import Macaroon

from l402.server import Authenticator, InvoiceProvider, MacaroonService, InvalidOrMissingL402Header, InvalidMacaroon


def test_encode_decode_identifier():
    version = 0
    payment_hash = "38caadbe0f6112d9b638e9ae24338f7e9bd930a3387100da776644e56965c9c1"
    token_id = os.urandom(32)

    # Create an instance of the Authenticator class
    authenticator = Authenticator(None, None, None)

    # Encode the identifier
    encoded_identifier = authenticator._encode_identifier(version, payment_hash, token_id)

    # Decode the identifier
    decoded_version, decoded_payment_hash, decoded_token_id = authenticator._decode_identifier(encoded_identifier)

    # Assert the decoded values match the original values
    assert decoded_version == version
    assert decoded_payment_hash == payment_hash
    assert decoded_token_id == token_id

def test_decode_macaroon_with_invalid_identifier_version():
    # Macaroon with identifier version 1 instead of 0
    encoded_macaroon = "AgENdGVzdF9sb2NhdGlvbgJCAAE4yq2-D2ES2bY46a4kM49-m9kwozhxANp3ZkTlaWXJwXZyiJia75BF20Jgzr50S8IDiA_VZxeAu-aZ2bjvAUgXAAAGIAV6MZ639CiOsOnQBNLRoonQIQkYd4KMPJDYlYFWmp-L"
    authenticator = Authenticator(None, None, None)

    # Assert that a ValueError is raised when encoding an identifier with an invalid version
    with pytest.raises(ValueError, match="Invalid L402 version"):
        authenticator._decode_macaroon(encoded_macaroon)

@pytest.mark.asyncio
async def test_new_challenge():
    # Mock the invoice provider and macaroon service
    payment_request = "lnbc..."
    payment_hash = "38caadbe0f6112d9b638e9ae24338f7e9bd930a3387100da776644e56965c9c1"
    mock_invoice_provider = AsyncMock(spec=InvoiceProvider)
    mock_invoice_provider.create_invoice.return_value = (payment_request, payment_hash)

    mock_macaroon_service = MagicMock(spec=MacaroonService)

    # L402 Challenge parameters
    location = "test_location"
    amount = 1000
    currency = "sats"
    description = "Test Challenge"

    # Create the authenticator
    authenticator = Authenticator(location, mock_invoice_provider, mock_macaroon_service)
    encoded_macaroon, returned_payment_request = await authenticator.new_challenge(amount, currency, description)

    # Assert the invoice provider was called with the correct arguments.
    mock_invoice_provider.create_invoice.assert_called_once_with(
        amount, currency, f"L402 Challenge: {description}"
    )
    assert mock_macaroon_service.insert_root_key.call_count == 1

    # Assert the macaroon service was called with the correct arguments.
    insert_root_key_args = mock_macaroon_service.insert_root_key.call_args[0]
    token_id, root_key, stored_encoded_macaroon = insert_root_key_args
    assert len(token_id) == 32
    assert len(root_key) == 32
    assert stored_encoded_macaroon == encoded_macaroon



    # Decode the macaroon and check the values
    mac, mac_payment_hash, mac_token_id = authenticator._decode_macaroon(encoded_macaroon)

    assert mac.location == location
    assert mac_payment_hash == payment_hash
    assert mac_token_id == token_id

    assert returned_payment_request == payment_request

def test_parse_l402_header():
    # Create an instance of the Authenticator class
    authenticator = Authenticator(None, None, None)

    # Test case 1: Valid L402 header
    valid_header = "L402 valid_macaroon:valid_preimage"
    encoded_macaroon, preimage = authenticator._parse_l402_header(valid_header)
    assert encoded_macaroon == "valid_macaroon"
    assert preimage == "valid_preimage"

    # Test case 2: Invalid L402 header format
    invalid_header_format = "Invalid header format"
    with pytest.raises(InvalidOrMissingL402Header, match=f"Invalid L402 header format: {invalid_header_format}"):
        authenticator._parse_l402_header(invalid_header_format)

    # Test case 3: Empty macaroon in L402 header
    empty_macaroon_header = "L402 :valid_preimage"
    with pytest.raises(InvalidOrMissingL402Header, match=f"Macaroon or preimage cannot be empty: {empty_macaroon_header}"):
        authenticator._parse_l402_header(empty_macaroon_header)

    # Test case 4: Empty preimage in L402 header
    empty_preimage_header = "L402 valid_macaroon:"
    with pytest.raises(InvalidOrMissingL402Header, match=f"Macaroon or preimage cannot be empty: {empty_preimage_header}"):
        authenticator._parse_l402_header(empty_preimage_header)

def test_validate_preimage():
    authenticator = Authenticator(None, None, None)
    payment_hash = "38caadbe0f6112d9b638e9ae24338f7e9bd930a3387100da776644e56965c9c1"

    # Valid preimage
    valid_preimage = "2f84e22556af9919f695d7761f404e98ff98058b7d32074de8c0c83bf63eecd7"
    authenticator._validate_preimage(valid_preimage, payment_hash)

    #  Invalid preimage
    invalid_preimage = "1111111111111111111111111111111111111111111111111111111111111111"
    with pytest.raises(ValueError, match="Invalid payment preimage"):
        authenticator._validate_preimage(invalid_preimage, payment_hash)


@pytest.mark.asyncio
async def test_validate_macaroon_success():
    # Create an instance of the Authenticator class with a mock MacaroonService
    mock_macaroon_service = AsyncMock()
    mock_macaroon_service.get_root_key.return_value = bytes.fromhex("d479a2f986756e35f0e0d8b2ea835a7dc3002b85d41d8fb20a027f2d2d0275c2")
    authenticator = Authenticator(None, None, mock_macaroon_service)

    # Test case 1: Valid macaroon
    token_id = "098a7cd3efe5f7b96250ba20b2fb64c351bb57402f7753756f4c55c1bce85ee3"
    encoded_macaroon = "AgENdGVzdF9sb2NhdGlvbgJCAAA4yq2-D2ES2bY46a4kM49-m9kwozhxANp3ZkTlaWXJwQmKfNPv5fe5YlC6ILL7ZMNRu1dAL3dTdW9MVcG86F7jAAAGIMSJ0L0eYt4Vlcdg3vNG1LmjvxNQxlufF0c15WFYpmgp"
    mac = Macaroon.deserialize(encoded_macaroon)
    await authenticator._validate_macaroon(mac, token_id)

@pytest.mark.asyncio
async def test_validate_macaroon_missing_token_id():
    # Create an instance of the Authenticator class with a mock MacaroonService
    mock_macaroon_service = AsyncMock()
    mock_macaroon_service.get_root_key.return_value = None
    authenticator = Authenticator(None, None, mock_macaroon_service)

    # Test case 2: Missing token_id in the database
    token_id = "missing_token_id"
    encoded_macaroon = "AgENdGVzdF9sb2NhdGlvbgJCAAA4yq2-D2ES2bY46a4kM49-m9kwozhxANp3ZkTlaWXJwQmKfNPv5fe5YlC6ILL7ZMNRu1dAL3dTdW9MVcG86F7jAAAGIMSJ0L0eYt4Vlcdg3vNG1LmjvxNQxlufF0c15WFYpmgp"
    mac = Macaroon.deserialize(encoded_macaroon)
    with pytest.raises(InvalidMacaroon, match="Macaroon verification failed."):
        await authenticator._validate_macaroon(mac, token_id)

@pytest.mark.asyncio
async def test_validate_macaroon_invalid_root_key():
    # Create an instance of the Authenticator class with a mock MacaroonService
    mock_macaroon_service = AsyncMock()
    mock_macaroon_service.get_root_key.return_value = bytes.fromhex("a479a2f986756e35f0e0d8b2ea835a7dc3002b85d41d8fb20a027f2d2d0275c2")
    authenticator = Authenticator(None, None, mock_macaroon_service)

    # Test case 3: Invalid root_key
    token_id = "098a7cd3efe5f7b96250ba20b2fb64c351bb57402f7753756f4c55c1bce85ee3"
    encoded_macaroon = "AgENdGVzdF9sb2NhdGlvbgJCAAA4yq2-D2ES2bY46a4kM49-m9kwozhxANp3ZkTlaWXJwQmKfNPv5fe5YlC6ILL7ZMNRu1dAL3dTdW9MVcG86F7jAAAGIMSJ0L0eYt4Vlcdg3vNG1LmjvxNQxlufF0c15WFYpmgp"
    mac = Macaroon.deserialize(encoded_macaroon)
    with pytest.raises(InvalidMacaroon, match="Macaroon verification failed."):
        await authenticator._validate_macaroon(mac, token_id)