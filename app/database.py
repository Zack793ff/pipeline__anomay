import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://chidizack24_db_user:IUUrwdBsKicpDB7F@cluster0.2sqi1ni.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)

DB_NAME = "anomaly_db"

# Force TLS for Render environment
client = AsyncIOMotorClient(
    MONGO_URI,
    tls=True,
    tlsAllowInvalidCertificates=False
)

db = client[DB_NAME]
