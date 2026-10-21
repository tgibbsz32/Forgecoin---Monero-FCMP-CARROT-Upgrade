"""ForgeCoin governance proof-of-concept API. Local testing only."""
import secrets
import time
from dataclasses import dataclass
from threading import RLock

import base58
from fastapi import FastAPI, Header, HTTPException
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey
from pydantic import BaseModel, Field
from services.governance_api import registry, applications, elections

app = FastAPI(title="ForgeCoin Governance Prototype", version="0.1.0")
LOCK = RLock()
CHALLENGE_TTL = 300
SESSION_TTL = 1800
AUDIENCE = "ForgeCoin governance development"
DOMAIN = "localhost"
ORIGIN = "http://localhost:8765"

@dataclass
class Challenge:
    address: str
    message: str
    expires: float

@dataclass
class Session:
    address: str
    expires: float

challenges: dict[str, Challenge] = {}
sessions: dict[str, Session] = {}
ELECTION_ROLES = {
    "staking": "staking",
    "miner": "miner",
    "developer": "developer",
    "community": "community",
    "chamber": "chamber",
}

class WalletRequest(BaseModel):
    address: str = Field(min_length=32, max_length=44)

class EligibilityApplication(BaseModel):
    role: str = Field(min_length=4, max_length=32)
    evidence_reference: str = Field(min_length=8, max_length=250)
    statement: str = Field(min_length=10, max_length=500)

class SignatureRequest(WalletRequest):
    nonce: str = Field(min_length=32, max_length=128)
    signature: str = Field(min_length=80, max_length=128)

def decode_pubkey(address: str) -> bytes:
    try:
        key = base58.b58decode(address)
        if len(key) != 32 or base58.b58encode(key).decode() != address:
            raise ValueError("invalid public key")
        return key
    except (ValueError, TypeError) as exc:
        raise HTTPException(400, "Invalid Solana public key") from exc

def authenticate(authorization: str | None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing session token")
    token = authorization[7:]
    with LOCK:
        session = sessions.get(token)
        if session is None or session.expires <= time.time():
            sessions.pop(token, None)
            raise HTTPException(401, "Invalid or expired session")
        return session.address

@app.get("/health")
def health():
    return {"status": "development-only", "binding_votes": False}

@app.post("/auth/challenge")
def challenge(request: WalletRequest):
    decode_pubkey(request.address)
    now = time.time()
    nonce = secrets.token_urlsafe(24)
    message = (
        f"{AUDIENCE}\nDomain: {DOMAIN}\nURI: {ORIGIN}\n"
        f"Wallet: {request.address}\nNonce: {nonce}\n"
        f"Issued At (unix seconds): {int(now)}\n"
        "Purpose: sign in only; no transaction or vote authorization"
    )
    with LOCK:
        challenges[nonce] = Challenge(request.address, message, now + CHALLENGE_TTL)
    return {"nonce": nonce, "message": message, "expires_in_seconds": CHALLENGE_TTL}

@app.post("/auth/verify")
def verify(request: SignatureRequest):
    public_key = decode_pubkey(request.address)
    try:
        sig = base58.b58decode(request.signature)
        if len(sig) != 64:
            raise ValueError("signature length")
    except (ValueError, TypeError) as exc:
        raise HTTPException(400, "Invalid Ed25519 signature encoding") from exc
    # Consume first under a lock; simultaneous submissions cannot reuse a nonce.
    with LOCK:
        pending = challenges.pop(request.nonce, None)
    if pending is None or pending.address != request.address or pending.expires <= time.time():
        raise HTTPException(401, "Challenge missing, expired or does not match wallet")
    try:
        VerifyKey(public_key).verify(pending.message.encode("utf-8"), sig)
    except (BadSignatureError, ValueError) as exc:
        raise HTTPException(401, "Invalid wallet signature") from exc
    token = secrets.token_urlsafe(32)
    registry.register(request.address)
    with LOCK:
        sessions[token] = Session(request.address, time.time() + SESSION_TTL)
    return {"access_token": token, "token_type": "bearer", "expires_in_seconds": SESSION_TTL}

@app.get("/me")
def me(authorization: str | None = Header(default=None)):
    address = authenticate(authorization)
    roles = sorted(registry.roles_for(address))
    return {"address": address, "verified_roles": roles, "votes_enabled": False}

@app.get("/elections/{election_id}/eligibility")
def eligibility(election_id: str, authorization: str | None = Header(default=None)):
    address = authenticate(authorization)
    if election_id not in ELECTION_ROLES:
        raise HTTPException(404, "Unknown election")
    required = ELECTION_ROLES[election_id]
    allowed_role = required in registry.roles_for(address)
    return {
        "election": election_id,
        "role_qualified": allowed_role,
        "ballot_enabled": False,
        "reason": "No binding election, snapshot or verified ballot registry is deployed",
    }

@app.post("/applications",status_code=201)
def create_application(request: EligibilityApplication, authorization: str | None = Header(default=None)):
    wallet=authenticate(authorization)
    try:
        application_id=applications.submit(wallet,request.role,request.evidence_reference,request.statement)
    except ValueError as exc:
        raise HTTPException(400,str(exc)) from exc
    return {"application_id":application_id,"status":"pending","votes_enabled":False}

@app.get("/applications/mine")
def my_applications(authorization: str | None = Header(default=None)):
    wallet=authenticate(authorization)
    return {"applications":applications.mine(wallet),"votes_enabled":False}

class PracticeBallot(BaseModel):
    choice: str = Field(pattern="^(yes|no|abstain)$")

@app.get("/practice-elections/{election_id}")
def practice_election(election_id: int):
    try:
        return elections.detail(election_id)
    except ValueError as exc:
        raise HTTPException(404,str(exc)) from exc

@app.post("/practice-elections/{election_id}/ballots", status_code=201)
def practice_vote(election_id: int, request: PracticeBallot,
                  authorization: str | None = Header(default=None)):
    wallet=authenticate(authorization)
    try:
        return elections.cast(election_id,wallet,request.choice)
    except PermissionError as exc:
        raise HTTPException(403,str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409,str(exc)) from exc
