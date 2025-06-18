from fastapi import APIRouter
from app.schema.word_schema import WordPublic
from app.db.mongodb import db
from app.constants import COLLECTION_NAME

router = APIRouter()

@router.get("/", response_model=list[WordPublic])
async def get_vocabulary(limit: int = 10, offset: int = 0):
    """
    Get a list of Māori vocabulary entries.

    - limit: maximum number of words to return (default: 10)
    - offset: number of entries to skip before starting to return results (default: 0)
    - If offset + limit exceeds the total count, wrap around from the start to fulfill the limit
    """
    total = await db[COLLECTION_NAME].count_documents({})  # Get total word count

    results = []

    if total == 0:
        return results  # Return empty list if no data

    # First batch: from `offset` to the end (or up to limit)
    first_batch_size = min(limit, total - offset)
    cursor1 = db[COLLECTION_NAME].find().skip(offset).limit(first_batch_size)
    async for word in cursor1:
        results.append({
            "id": str(word["_id"]),
            "maori": word["maori"],
            "english": word["english"]
        })

    # If needed, get second batch from the beginning
    remaining = limit - len(results)
    if remaining > 0:
        cursor2 = db[COLLECTION_NAME].find().limit(remaining)
        async for word in cursor2:
            results.append({
                "id": str(word["_id"]),
                "maori": word["maori"],
                "english": word["english"]
            })

    return results
