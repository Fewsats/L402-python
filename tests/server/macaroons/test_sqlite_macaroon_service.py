import os
import sqlite3
import pytest
from datetime import datetime
from l402.server.macaroons import SqliteMacaroonService

@pytest.fixture
def macaroon_service():
    service = SqliteMacaroonService(":memory:")
    yield service
    service.conn.close()

@pytest.mark.asyncio
async def test_insert_and_get_root_key(macaroon_service):
    token_id = os.urandom(32)
    root_key = os.urandom(32)
    macaroon = "encoded_macaroon"

    await macaroon_service.insert_root_key(token_id, root_key, macaroon)

    retrieved_root_key = await macaroon_service.get_root_key(token_id)
    assert retrieved_root_key == root_key

@pytest.mark.asyncio
async def test_get_non_existent_root_key(macaroon_service):
    non_existent_token_id = os.urandom(32)

    retrieved_root_key = await macaroon_service.get_root_key(non_existent_token_id)
    assert retrieved_root_key is None

@pytest.mark.asyncio
async def test_insert_multiple_root_keys(macaroon_service):
    token_id1 = os.urandom(32)
    root_key1 = os.urandom(32)
    macaroon1 = "encoded_macaroon1"

    token_id2 = os.urandom(32)
    root_key2 = os.urandom(32)
    macaroon2 = "encoded_macaroon2"

    await macaroon_service.insert_root_key(token_id1, root_key1, macaroon1)
    await macaroon_service.insert_root_key(token_id2, root_key2, macaroon2)

    retrieved_root_key1 = await macaroon_service.get_root_key(token_id1)
    assert retrieved_root_key1 == root_key1

    retrieved_root_key2 = await macaroon_service.get_root_key(token_id2)
    assert retrieved_root_key2 == root_key2

def test_create_table(macaroon_service):
    cursor = macaroon_service.conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='macaroons'")
    table_exists = cursor.fetchone() is not None
    assert table_exists

def test_adapt_datetime():
    dt = datetime.now()
    adapted_dt = sqlite3.adapt(dt)
    assert isinstance(adapted_dt, str)
    assert adapted_dt == dt.isoformat()