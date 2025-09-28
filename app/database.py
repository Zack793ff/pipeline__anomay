import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

# Correct format 
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://chidizack24_db_user:IUUrwdBsKicpDB7F@cluster0.2sqi1ni.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)

DB_NAME = "anomaly_db"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

