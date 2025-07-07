from app.constants import COLLECTION_USERS

async def create_indexes(db):
    await db[COLLECTION_USERS].create_index("username", unique=True)
    await db[COLLECTION_USERS].create_index("email", unique=True)
