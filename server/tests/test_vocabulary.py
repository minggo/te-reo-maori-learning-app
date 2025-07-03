import pytest 

@pytest.mark.asyncio
async def test_get_vocabulary_empty(clear_test_db, client):
    r = await client.get("/vocabulary/", params={"limit": 5, "offset": 0})
    assert r.status_code == 200
    assert r.json() == []

@pytest.mark.asyncio
async def test_get_vocabulary_from_file(client, seed_data):
    r = await client.get("/vocabulary/", params={"limit": 5, "offset": 0})
    assert r.status_code == 200

    body = r.json()
    assert len(body) == 5
    
    for i, doc in enumerate(seed_data[:5]):
        assert body[i]["maori"] == doc["maori"]
        assert body[i]["english"] == doc["english"]

@pytest.mark.asyncio
async def test_get_vocabulary_wraps_to_start_when_offset_exceeds_length(client, seed_data):
    total = len(seed_data)
    limit = 5
    offset = total - 2

    r = await client.get("/vocabulary/", params={"limit": limit, "offset": offset})
    assert r.status_code == 200

    body = r.json()
    assert len(body) == limit

    for i in range(limit):
        expected_index = (offset + i) % total
        assert body[i]["maori"] == seed_data[expected_index]["maori"]
        assert body[i]["english"] == seed_data[expected_index]["english"]   

    