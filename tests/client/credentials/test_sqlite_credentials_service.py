import pytest
from l402.client.credentials import L402Credentials, SqliteCredentialsService

@pytest.fixture(params=[SqliteCredentialsService(":memory:")])
def db(request):
    return request.param

def test_store_and_get_credentials(db):
    credentials = L402Credentials("macaroon", "preimage", "invoice")
    credentials.set_location("https://example.com")
    db.store(credentials)

    retrieved_credentials = db.get("https://example.com")
    assert retrieved_credentials is not None
    assert retrieved_credentials.macaroon == "macaroon"
    assert retrieved_credentials.preimage == "preimage"
    assert retrieved_credentials.invoice == "invoice"
    assert retrieved_credentials.location == "https://example.com"

def test_get_non_existent_credentials(db):
    retrieved_credentials = db.get("https://nonexistent.com")
    assert retrieved_credentials is None

def test_store_multiple_credentials(db):
    credentials1 = L402Credentials("macaroon1", "preimage1", "invoice1")
    credentials1.set_location("https://example.com")
    db.store(credentials1)

    credentials2 = L402Credentials("macaroon2", "preimage2", "invoice2")
    credentials2.set_location("https://example.com")
    db.store(credentials2)

    retrieved_credentials = db.get("https://example.com")
    assert retrieved_credentials is not None
    assert retrieved_credentials.macaroon == "macaroon2"
    assert retrieved_credentials.preimage == "preimage2"
    assert retrieved_credentials.invoice == "invoice2"

def test_store_different_locations(db):
    credentials1 = L402Credentials("macaroon1", "preimage1", "invoice1")
    credentials1.set_location("https://example1.com")
    db.store(credentials1)

    credentials2 = L402Credentials("macaroon2", "preimage2", "invoice2")
    credentials2.set_location("https://example2.com")
    db.store(credentials2)

    retrieved_credentials1 = db.get("https://example1.com")
    assert retrieved_credentials1 is not None
    assert retrieved_credentials1.macaroon == "macaroon1"

    retrieved_credentials2 = db.get("https://example2.com")
    assert retrieved_credentials2 is not None
    assert retrieved_credentials2.macaroon == "macaroon2"