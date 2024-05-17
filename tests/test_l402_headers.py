# test_headers.py

import pytest
from l402.common.headers import L402HeaderV0, parse_l402_challenge_header
from l402.common.exceptions import UnsupportedVersionError, InvalidL402HeaderError
from l402.common.constants import L402_VERSION_0, PARAM_MACAROON, PARAM_INVOICE

def test_l402_header_v0():
    macaroon = "some_macaroon"
    invoice = "some_invoice"
    header = L402HeaderV0(macaroon, invoice)

    assert header.version() == L402_VERSION_0
    assert header.credentials() == macaroon
    assert header.payment_request() == invoice
    assert header.parameter(PARAM_MACAROON) == macaroon
    assert header.parameter(PARAM_INVOICE) == invoice
    assert header.get_parameters() == {
        PARAM_VERSION: L402_VERSION_0,
        PARAM_MACAROON: macaroon,
        PARAM_INVOICE: invoice,
    }
    assert str(header) == f"L402 version={L402_VERSION_0} {PARAM_MACAROON}={macaroon} {PARAM_INVOICE}={invoice}"

def test_parse_l402_challenge_header_valid_v0():
    header_value = f"L402 version={L402_VERSION_0} {PARAM_MACAROON}=some_macaroon {PARAM_INVOICE}=some_invoice"
    header = parse_l402_challenge_header(header_value)

    assert isinstance(header, L402HeaderV0)
    assert header.version() == L402_VERSION_0
    assert header.credentials() == "some_macaroon"
    assert header.payment_request() == "some_invoice"

def test_parse_l402_challenge_header_invalid_scheme():
    header_value = "InvalidScheme version=0 macaroon=some_macaroon invoice=some_invoice"
    with pytest.raises(InvalidL402HeaderError):
        parse_l402_challenge_header(header_value)

def test_parse_l402_challenge_header_missing_version():
    header_value = "L402 macaroon=some_macaroon invoice=some_invoice"
    with pytest.raises(InvalidL402HeaderError):
        parse_l402_challenge_header(header_value)

def test_parse_l402_challenge_header_unsupported_version():
    header_value = "L402 version=999 macaroon=some_macaroon invoice=some_invoice"
    with pytest.raises(UnsupportedVersionError):
        parse_l402_challenge_header(header_value)

def test_parse_l402_challenge_header_missing_macaroon():
    header_value = f"L402 version={L402_VERSION_0} invoice=some_invoice"
    with pytest.raises(InvalidL402HeaderError):
        parse_l402_challenge_header(header_value)

def test_parse_l402_challenge_header_missing_invoice():
    header_value = f"L402 version={L402_VERSION_0} macaroon=some_macaroon"
    with pytest.raises(InvalidL402HeaderError):
        parse_l402_challenge_header(header_value)