from app.db.mongodb import db
from app.constants import COLLECTION_NAME
import json
from pathlib import Path

async def import_words_if_empty():
    existing_count = await db[COLLECTION_NAME].count_documents({})
    if existing_count > 0:
        print(f"📦 Database already contains {existing_count} words. Skipping import.")
        return

    base_dir = Path(__file__).resolve().parent.parent
    json_path = base_dir / "data" / "words.json"
    with open(json_path) as f:
        data = json.load(f)

    await db[COLLECTION_NAME].insert_many(data)
    print(f"✅ Imported {len(data)} words into MongoDB.")
