from typing import List
from fastapi import APIRouter, Depends
from datetime import datetime, timezone
from pymongo import ReturnDocument
from .models import WellData
from .database import db
from .auth import create_jwt, verify_jwt  
from .auth_challenge import router as challenge_router

# MongoDB collections
data_collection = db["well_data"]
counter_collection = db["counters"]

router = APIRouter()

# === Register the challenge-response router ===
router.include_router(challenge_router, prefix="/auth")  


# Issue token once (then hardcode in ESP32 firmware)
@router.post("/login")
async def login(device_id: str):
    token = create_jwt(device_id)
    return {"access_token": token}

@router.post("/upload", response_model=WellData)
async def upload_data(payload: WellData, user=Depends(verify_jwt)):
    if not payload.timestamp:
        payload.timestamp = datetime.now(timezone.utc)

    generated_id = await get_next_sequence("well_data_id")
    payload.id = generated_id

    doc = payload.model_dump(by_alias=True)
    doc["_id"] = generated_id

    await data_collection.insert_one(doc)
    return payload


@router.get("/all", response_model=List[WellData])
async def get_all_data(limit: int = 50, user=Depends(verify_jwt)):
    docs = await data_collection.find().sort("_id", -1).to_list(length=limit)
    return [WellData(**doc) for doc in docs]


# Optional: keep /login for legacy purposes
@router.post("/login")
async def login(device_id: str):
    from .auth import create_jwt
    token = create_jwt(device_id)
    return {"access_token": token}

async def get_next_sequence(name: str):
    count = await data_collection.estimated_document_count()
    if count == 0:
        await counter_collection.update_one(
            {"_id": name},
            {"$set": {"seq": 0}},
            upsert=True
        )

    seq_doc = await counter_collection.find_one_and_update(
        {"_id": name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    return seq_doc["seq"]
