from datetime import datetime, timedelta
from fastapi import APIRouter, Query
from typing import List
from app.schema.word_schema import WordPublic
from app.schema.user_learned_schema import UserLearnedWords
from app.db.mongodb import db
from app.constants import (
    COLLECTION_NAME,
    COLLECTION_USER_LEARNED,
    COLLECTION_USER_MISTAKES,
)

router = APIRouter()

async def get_due_mistake_word_ids(user_id: str, now: datetime) -> List[str]:
    """
    Fetch the list of mistake word IDs that are due for review according to the memory curve.
    """
    doc = await db[COLLECTION_USER_MISTAKES].find_one({"_id": user_id})
    if not doc or "wrong_words" not in doc:
        return []
    result = []
    for w in doc["wrong_words"]:
        last = w.get("last_wrong")
        count = w.get("count", 0)
        # Simple memory curve for demo: higher count = longer interval
        if count >= 3:
            interval = timedelta(days=7)
        elif count == 2:
            interval = timedelta(days=3)
        else:
            interval = timedelta(days=1)
        if last and now - last >= interval:
            result.append(w["id"])
    return result

async def get_learned_ids(user_id: str) -> set:
    """
    Fetch the set of learned word IDs for the given user.
    """
    raw = await db[COLLECTION_USER_LEARNED].find_one({"_id": user_id})
    if raw:
        user_learned = UserLearnedWords.model_validate(raw)
        return set(user_learned.learned_ids)
    else:
        return set()

async def add_learned_ids(user_id: str, new_word_ids: List[str]):
    """
    Add the given word IDs to the user's learned words in the database.
    """
    await db[COLLECTION_USER_LEARNED].update_one(
        {"_id": user_id},
        {"$addToSet": {"learned_ids": {"$each": new_word_ids}}},
        upsert=True
    )

@router.get("/", response_model=List[WordPublic])
async def get_vocabulary(
    user_id: str = "anonymous",
    limit: int = Query(10, ge=1, le=100, description="Number of words to return")
):
    """
    Returns a list of words for the user to study.

    Rules:
    - 20% (rounded up) from the user's mistake book that are due for review (memory curve).
    - Remaining: fill with unlearned words.
    - If still not enough, fill with already learned words (excluding mistake words already used).

    All returned words are marked as learned for the user.
    """
    now = datetime.utcnow()
    results = []
    used_ids = set()

    # 1. Select 20% mistake words due for review
    due_mistake_ids = await get_due_mistake_word_ids(user_id, now)
    n_mistake = max(1, int(limit * 0.2))  # At least 1 if there are any due
    selected_mistakes = due_mistake_ids[:n_mistake]
    if selected_mistakes:
        cursor = db[COLLECTION_NAME].find({"_id": {"$in": selected_mistakes}})
        async for word in cursor:
            results.append({
                "id": str(word["_id"]),
                "maori": word["maori"],
                "english": word["english"]
            })
            used_ids.add(str(word["_id"]))
            if len(results) >= n_mistake:
                break

    # 2. Fill with unlearned words
    if len(results) < limit:
        learned_ids = await get_learned_ids(user_id)
        unseen_cursor = db[COLLECTION_NAME].find({"_id": {"$nin": list(learned_ids | used_ids)}}).limit(limit - len(results))
        async for word in unseen_cursor:
            results.append({
                "id": str(word["_id"]),
                "maori": word["maori"],
                "english": word["english"]
            })
            used_ids.add(str(word["_id"]))
            if len(results) >= limit:
                break

    # 3. If still not enough, fill with already learned (but not mistake) words
    if len(results) < limit:
        fill_cursor = db[COLLECTION_NAME].find({"_id": {"$nin": list(used_ids)}}).limit(limit - len(results))
        async for word in fill_cursor:
            results.append({
                "id": str(word["_id"]),
                "maori": word["maori"],
                "english": word["english"]
            })
            used_ids.add(str(word["_id"]))
            if len(results) >= limit:
                break

    # 4. Mark all returned words as learned for this user
    await add_learned_ids(user_id, [r["id"] for r in results])

    return results
