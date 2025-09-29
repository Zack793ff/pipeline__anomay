import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument
import os

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://chidizack24_db_user:IUUrwdBsKicpDB7F@cluster0.2sqi1ni.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)

DB_NAME = "anomaly_db"

client = AsyncIOMotorClient(
    MONGO_URI,
    tls=True,
    tlsAllowInvalidCertificates=False
)

db = client[DB_NAME]

async def get_next_sequence(name: str) -> int:
    well_data_collection = db["well_data"]
    counters_collection = db["counters"]

    # If well_data collection is empty, reset the counter
    if await well_data_collection.estimated_document_count() == 0:
        await counters_collection.update_one(
            {"_id": name},
            {"$set": {"seq": 0}},
            upsert=True
        )

    counter = await counters_collection.find_one_and_update(
        {"_id": name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )

    return int(counter["seq"])

