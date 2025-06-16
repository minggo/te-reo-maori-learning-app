from fastapi import APIRouter
from app.schema.word_schema import WordPublic
from app.db.mongodb import db
from app.constants import COLLECTION_NAME

router = APIRouter()

@router.get("/", response_model=list[WordPublic])
async def get_vocabulary(limit: int = 10, offset: int = 0):
    cursor = db[COLLECTION_NAME].find().skip(offset).limit(limit)
    results = []
    async for word in cursor:
        results.append({
            "id": str(word["_id"]),
            "maori": word["maori"],
            "english": word["english"]
        })
    return results