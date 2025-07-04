import pytest 

@pytest.mark.asyncio
async def test_get_vocabulary_empty(clear_test_db, client):
    r = await client.get("/vocabulary/", params={"user_id": "anonymous", "limit": 5})
    assert r.status_code == 200
    assert r.json() == []

@pytest.mark.asyncio
async def test_get_vocabulary_from_file(client, seed_data):
    r = await client.get("/vocabulary/", params={"user_id": "anonymous", "limit": 5})
    assert r.status_code == 200

    body = r.json()
    assert len(body) == 5
    
    for i, doc in enumerate(seed_data[:5]):
        assert body[i]["maori"] == doc["maori"]
        assert body[i]["english"] == doc["english"]   

    