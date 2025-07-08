import pytest 
from datetime import datetime, timedelta
import math
from app.constants import (
    COLLECTION_NAME,
    COLLECTION_USER_LEARNED,
    COLLECTION_USER_MISTAKES,
)
from app.core.config import settings

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

@pytest.mark.asyncio
async def test_get_vocabulary_priority_rules(clear_test_db, client, db_client, seed_data):
    """
    Verify get_vocabulary obeys the three rules in order:
    1) First ceil(limit * 0.2) items are due mistakes;
    2) Next items are unlearned words (neither mistakes nor learned);
    3) Finally fill with learned words only if unlearned were insufficient.
    """
    user_id = "test_user"
    limit = 10
    now = datetime.utcnow()

    # seed IDs
    seed_ids = [str(doc["_id"]) for doc in seed_data]

    # 1) Mistake book: 3 due, 2 not due
    due_ids = seed_ids[:3]
    not_due_ids = seed_ids[3:5]
    mistakes = []
    for _id in due_ids:
        mistakes.append({"id": _id, "last_wrong": now - timedelta(days=2), "count": 1})
    for _id in not_due_ids:
        mistakes.append({"id": _id, "last_wrong": now, "count": 1})
    await db_client[settings.DB_NAME][COLLECTION_USER_MISTAKES].insert_one({
        "_id": user_id,
        "wrong_words": mistakes
    })

    # 2) Learned IDs (won't be needed here because unlearned are enough)
    learned_ids = set(seed_ids[5:8])
    await db_client[settings.DB_NAME][COLLECTION_USER_LEARNED].insert_one({
        "_id": user_id, "learned_ids": list(learned_ids)
    })

    # call endpoint
    response = await client.get("/vocabulary/", params={"user_id": user_id, "limit": limit})
    assert response.status_code == 200
    results = response.json()
    assert len(results) == limit

    # expected mistake count
    expected_mistakes = math.ceil(limit * 0.2)

    # 1) First segment = due mistakes
    first = [item["id"] for item in results[:expected_mistakes]]
    assert all(_id in due_ids for _id in first)
    assert not any(_id in not_due_ids for _id in first)

    # 2) Middle segment = truly unlearned
    middle = [item["id"] for item in results[expected_mistakes:]]
    # None of these should be in due_ids or learned_ids
    assert all(_id not in due_ids for _id in middle)
    assert all(_id not in learned_ids for _id in middle)

    # 3) Since there were plenty of unlearned, no learned words should appear
    last_segment = [item["id"] for item in results if item["id"] in learned_ids]
    assert last_segment == [], "Learned words only appear if unlearned pool was insufficient"
    