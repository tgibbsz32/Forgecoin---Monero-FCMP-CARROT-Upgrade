"""Offline share verification boundary. Never credits payouts or submits blocks.

A caller MUST supply a trusted digest-producing verifier for the canonical job
hashing blob; no production RandomX adapter is connected by this module.
The opaque verifier returns a 32-byte digest, not a miner-provided hash.
"""
from dataclasses import dataclass
from typing import Callable
from .share_preflight import SharePreflight

MAX_HASH=(1<<256)-1
MAX_DIFFICULTY=(1<<128)-1

class VerificationError(ValueError):
    pass

@dataclass(frozen=True)
class VerificationResult:
    status: str
    digest_hex: str | None = None

def verify_offline_share(
    preflight: SharePreflight,
    job_id: str,
    nonce_hex: str,
    current_height: int,
    hashing_blob: bytes,
    nonce_offset: int,
    worker_difficulty: int,
    verifier: Callable[[bytes], bytes] | None = None,
) -> VerificationResult:
    # No verifier means NO success path; does not consume a nonce.
    if verifier is None or not callable(verifier):
        raise VerificationError("trusted RandomX verifier not configured")
    if type(worker_difficulty) is not int or not 1 <= worker_difficulty <= MAX_DIFFICULTY:
        raise VerificationError("invalid worker difficulty")
    if type(nonce_offset) is not int or nonce_offset < 0:
        raise VerificationError("invalid nonce offset")
    if not isinstance(hashing_blob, bytes) or nonce_offset+4 > len(hashing_blob):
        raise VerificationError("invalid hashing blob")
    preflight.inspect(job_id,nonce_hex,current_height)
    nonce=bytes.fromhex(nonce_hex)
    work=hashing_blob[:nonce_offset]+nonce+hashing_blob[nonce_offset+4:]
    try:
        digest=verifier(work)
    except Exception as exc:
        raise VerificationError("trusted verifier failed") from exc
    if not isinstance(digest, bytes) or len(digest)!=32:
        raise VerificationError("trusted verifier returned invalid digest")
    if int.from_bytes(digest,"little") > MAX_HASH//worker_difficulty:
        return VerificationResult("LOW_DIFFICULTY")
    # Deliberately NOT ACCEPTED: actual RandomX integration, canonical template
    # checks, concurrency persistence and payout ledger remain incomplete.
    return VerificationResult("POW_THRESHOLD_MET_UNCREDITED",digest.hex())
