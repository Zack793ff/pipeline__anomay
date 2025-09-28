from time import timezone
from fastapi import APIRouter
from datetime import datetime
from .models import WellData
from .database import db
from bson import ObjectId


# Define MongoDB collection
data_collection = db["well_data"]

router = APIRouter()

@router.post("/upload")
async def upload_data(payload: WellData):
    """
    Receive JSON data from ESP32 and store in MongoDB.
    Uses WellData Pydantic model for validation.
    """
    # Convert to dict with aliases so MongoDB keeps original keys
    doc = payload.model_dump(by_alias=True)

    # Add timestamp if missing
    if not doc.get("timestamp"):
        doc["timestamp"] = datetime.now(timezone.utc).isoformat()

    # Generate Integer ID
    doc["_id"] = await get_next_sequence("well_data_id")

    # Insert into MongoDB
    result = await data_collection.insert_one(doc)
    return {"status": "success", "id": str(result.inserted_id)}

@router.get("/all")
async def get_all_data(limit: int = 50):
    """
    Retrieve last 'limit' documents from MongoDB.
    Default = 50.
    Ordered by numeric _id (latest first).
    """
    docs = await data_collection.find().sort("_id", -1).to_list(limit)
    
    # Convert ObjectId to string for JSON serialization
    for doc in docs:
        doc["_id"] = str(doc["_id"])

    return {"data": docs}


async def get_next_sequence(name: str):
    counter = db["counters"]
    seq_doc = await counter.find_one_and_update(
        {"_id": name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True
    )

    return seq_doc["seq"]

