from fastapi import APIRouter
from app.schema.word_schema import WordPublic
from app.db.mongodb import db
from app.constants import COLLECTION_NAME

router = APIRouter()

@router.get("/", response_model=list[WordPublic])
async def get_vocabulary(limit: int = 10, offset: int = 0):
    """
    Fetch a list of Māori vocabulary entries with circular pagination support.

    Parameters:
    - limit (int): The number of entries to return (minimum 1, default 10).
    - offset (int): The number of entries to skip before starting. If offset exceeds
      the total number of documents, it wraps around using modulo logic.

    Behavior:
    - If `offset + limit` goes beyond the end of the collection, the function
      wraps around to the beginning to fulfill the full `limit` count.
    - Uses `estimated_document_count()` for fast approximate total count.
    """
    total = await db[COLLECTION_NAME].estimated_document_count({})  # Get total word count
    limit = max(1, min(limit, total))  # Ensure limit is between 1 and total
    offset = max(0, offset)  # Ensure offset is non-negative

    results = []

    if total == 0:
        return results  # Return empty list if no data
    
    offset = offset % total  # Wrap around offset if it exceeds total

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
