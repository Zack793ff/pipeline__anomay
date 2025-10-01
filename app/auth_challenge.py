from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import secrets, base64, jwt, time
from datetime import datetime, timezone, timedelta
from typing import Dict

from app.models import ChallengeRequest, ChallengeResponse

router = APIRouter()

# Store device public keys (for demo, can be plain dict)
DEVICE_PUBLIC_KEYS: Dict[str, str] = {
    "device123": "your_public_key_here"  # PEM format
}

# Temporary storage of challenges: device_id -> nonce
CHALLENGES: Dict[str, bytes] = {}

SECRET_KEY = "supersecretjwtkey123"
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 1


# Request a challenge
@router.post("/request_challenge")
async def request_challenge(req: ChallengeRequest):
    if req.device_id not in DEVICE_PUBLIC_KEYS:
        raise HTTPException(status_code=400, detail="Unknown device")
    nonce = secrets.token_bytes(32)
    CHALLENGES[req.device_id] = nonce
    return {"challenge": nonce.hex()}

# Verify signature and issue short-lived JWT
@router.post("/verify_challenge")
async def verify_challenge(resp: ChallengeResponse):
    if resp.device_id not in DEVICE_PUBLIC_KEYS or resp.device_id not in CHALLENGES:
        raise HTTPException(status_code=400, detail="Invalid request")

    nonce = CHALLENGES.pop(resp.device_id)
    public_key_pem = DEVICE_PUBLIC_KEYS[resp.device_id].encode()

    # Load public key
    from cryptography.hazmat.primitives import serialization, hashes
    from cryptography.hazmat.primitives.asymmetric import padding, ec
    from cryptography.exceptions import InvalidSignature

    public_key = serialization.load_pem_public_key(public_key_pem)
    signature = base64.b64decode(resp.signature)

    try:
        if isinstance(public_key, ec.EllipticCurvePublicKey):
            public_key.verify(signature, nonce, ec.ECDSA(hashes.SHA256()))
        else:
            # fallback: RSA
            public_key.verify(signature, nonce, padding.PKCS1v15(), hashes.SHA256())
    except InvalidSignature:
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Success → issue JWT
    expire = datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS)
    payload = {"sub": resp.device_id, "exp": expire.timestamp()}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return {"token": token, "exp": int(expire.timestamp())}
