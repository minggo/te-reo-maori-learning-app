import os
import pymongo
import time
import sys

uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
while True:
    try:
        client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=2000)
        client.admin.command("ping")
        print("MongoDB is up ✓")
        sys.exit(0)
    except Exception:
        print("Waiting for MongoDB…")
        time.sleep(2)
