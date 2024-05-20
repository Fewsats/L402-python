import pytest
from datetime import datetime
from l402.credentials import L402Credentials, MemoryStore, SqliteStore

@pytest.fixture(params=[MemoryStore(), SqliteStore(":memory:")])
def store(request):
    return request.param

def test_insert_and_get_credentials(store):
    credentials = L402Credentials("macaroon", "preimage", "invoice")
    credentials.set_location("https://example.com")
    store.insert(credentials)

    retrieved_credentials = store.get("https://example.com")
    assert retrieved_credentials is not None
    assert retrieved_credentials.macaroon == "macaroon"
    assert retrieved_credentials.preimage == "preimage"
    assert retrieved_credentials.invoice == "invoice"
    assert retrieved_credentials.location == "https://example.com"

def test_get_non_existent_credentials(store):
    retrieved_credentials = store.get("https://nonexistent.com")
    assert retrieved_credentials is None

def test_insert_multiple_credentials(store):
    credentials1 = L402Credentials("macaroon1", "preimage1", "invoice1")
    credentials1.set_location("https://example.com")
    store.insert(credentials1)

    credentials2 = L402Credentials("macaroon2", "preimage2", "invoice2")
    credentials2.set_location("https://example.com")
    store.insert(credentials2)

    retrieved_credentials = store.get("https://example.com")
    assert retrieved_credentials is not None
    assert retrieved_credentials.macaroon == "macaroon2"
    assert retrieved_credentials.preimage == "preimage2"
    assert retrieved_credentials.invoice == "invoice2"

def test_insert_different_locations(store):
    credentials1 = L402Credentials("macaroon1", "preimage1", "invoice1")
    credentials1.set_location("https://example1.com")
    store.insert(credentials1)

    credentials2 = L402Credentials("macaroon2", "preimage2", "invoice2")
    credentials2.set_location("https://example2.com")
    store.insert(credentials2)

    retrieved_credentials1 = store.get("https://example1.com")
    assert retrieved_credentials1 is not None
    assert retrieved_credentials1.macaroon == "macaroon1"

    retrieved_credentials2 = store.get("https://example2.com")
    assert retrieved_credentials2 is not None
    assert retrieved_credentials2.macaroon == "macaroon2"