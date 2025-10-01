from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import secrets, base64, jwt
from datetime import datetime, timezone, timedelta
from typing import Dict

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec, padding
from cryptography.exceptions import InvalidSignature

router = APIRouter()

# ----- Models -----
class ChallengeRequest(BaseModel):
    device_id: str

class ChallengeResponse(BaseModel):
    device_id: str
    signature: str  # base64-encoded

# ----- Server configuration -----
SECRET_KEY = "supersecretjwtkey123"
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 1

# ----- Device public keys (PEM) -----
DEVICE_PUBLIC_KEYS: Dict[str, str] = {
    "device123": """-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEmZSmXgF0+TAbjJBMV9gzH4bNsuNb
+Ue9qb4YJ3VleoyepLkE7WOe7SE8CHzgJ0alPRFenM9M7KFSky+gyUMXeQ==
-----END PUBLIC KEY-----"""
}


# ----- Temporary challenge storage -----
CHALLENGES: Dict[str, bytes] = {}

# ----- Routes -----
@router.post("/request_challenge")
async def request_challenge(req: ChallengeRequest):
    if req.device_id not in DEVICE_PUBLIC_KEYS:
        raise HTTPException(status_code=400, detail="Unknown device")

    nonce = secrets.token_bytes(32)
    CHALLENGES[req.device_id] = nonce
    return {"challenge": nonce.hex()}


@router.post("/verify_challenge")
async def verify_challenge(resp: ChallengeResponse):
    if resp.device_id not in DEVICE_PUBLIC_KEYS or resp.device_id not in CHALLENGES:
        raise HTTPException(status_code=400, detail="Invalid request")

    nonce = CHALLENGES.pop(resp.device_id)
    public_key_pem = DEVICE_PUBLIC_KEYS[resp.device_id].encode()
    public_key = serialization.load_pem_public_key(public_key_pem)

    signature = base64.b64decode(resp.signature)

    try:
        if isinstance(public_key, ec.EllipticCurvePublicKey):
            public_key.verify(signature, nonce, ec.ECDSA(hashes.SHA256()))
        else:
            public_key.verify(signature, nonce, padding.PKCS1v15(), hashes.SHA256())
    except InvalidSignature:
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Success → issue JWT
    expire = datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS)
    payload = {"sub": resp.device_id, "exp": int(expire.timestamp())}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {"token": token, "exp": int(expire.timestamp())}
