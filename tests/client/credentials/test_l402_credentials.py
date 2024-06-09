import pytest
from l402.client.credentials import L402Credentials, parse_http_402_response, _parse_l402_challenge
from unittest.mock import Mock

def test_l402credentials_initialization():
    macaroon = "test_macaroon"
    preimage = "test_preimage"
    invoice = "test_invoice"
    
    credentials = L402Credentials(macaroon, preimage, invoice)
    
    assert credentials.macaroon == macaroon
    assert credentials.preimage == preimage
    assert credentials.invoice == invoice

def test_authentication_header():
    macaroon = "test_macaroon"
    preimage = "test_preimage"
    invoice = "test_invoice"
    
    credentials = L402Credentials(macaroon, preimage, invoice)
    
    assert credentials.authentication_header() == f"L402 {macaroon}:{preimage}"

def test_parse_http_402_response_success():
    macaroon = "test_macaroon"
    invoice = "test_invoice"
    challenge = f'L402 macaroon="{macaroon}", invoice="{invoice}"'
    
    mock_response = Mock()
    mock_response.headers = {'WWW-Authenticate': challenge}
    
    credentials = parse_http_402_response(mock_response)
    
    assert credentials.macaroon == macaroon
    assert credentials.preimage is None
    assert credentials.invoice == invoice

def test_parse_http_402_response_missing_header():
    mock_response = Mock()
    mock_response.headers = {}
    
    with pytest.raises(ValueError, match="WWW-Authenticate header missing."):
        parse_http_402_response(mock_response)

def test_parse_l402_challenge_success():
    macaroon = "test_macaroon"
    invoice = "test_invoice"
    challenge = f'L402 macaroon="{macaroon}", invoice="{invoice}"'
    
    credentials = _parse_l402_challenge(challenge)
    
    assert credentials.macaroon == macaroon
    assert credentials.preimage is None
    assert credentials.invoice == invoice

def test_parse_l402_challenge_missing_macaroon():
    invoice = "test_invoice"
    challenge = f'L402 invoice="{invoice}"'
    
    with pytest.raises(ValueError, match="Challenge parsing failed"):
        _parse_l402_challenge(challenge)

def test_parse_l402_challenge_missing_invoice():
    macaroon = "test_macaroon"
    challenge = f'L402 macaroon="{macaroon}"'
    
    with pytest.raises(ValueError, match="Challenge parsing failed"):
        _parse_l402_challenge(challenge)