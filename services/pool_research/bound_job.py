"""Offline template-bound share research, without credits or network I/O.

Call register with a locally validated daemon template; subsequent submissions
provide only job ID and nonce, never a blob, target or nonce offset.
"""
from dataclasses import dataclass, field
from hashlib import sha256
from threading import Lock
from typing import Callable
from .template_adapter import Template
from .share_preflight import SharePreflight, SharePreflightError
from .pow_boundary import VerificationError, VerificationResult, MAX_HASH, MAX_DIFFICULTY

def _varint(data: bytes, start: int):
    value=0
    for i in range(10):
        p=start+i
        if p>=len(data):raise VerificationError("truncated header")
        b=data[p]
        if i==9 and b>1:raise VerificationError("varint overflow")
        value|=(b&127)<<(i*7)
        if b<128:
            if i and value < (1<<(7*i)):raise VerificationError("noncanonical varint")
            return p+1
    raise VerificationError("header varint too long")

@dataclass(frozen=True)
class BoundWork:
    height: int
    blob: bytes
    nonce_offset: int
    seed: bytes
    worker_difficulty: int

class BoundJobVerifier:
    """Single-process research store; caller must trust its template source."""
    def __init__(self):
        self._lock=Lock()
        self._preflight=SharePreflight()
        self._jobs: dict[str,BoundWork]={}

    def register(self, template: Template, worker_difficulty: int) -> str:
        if not isinstance(template,Template):
            raise VerificationError("validated template required")
        if type(worker_difficulty) is not int or not 1<=worker_difficulty<=MAX_DIFFICULTY:
            raise VerificationError("invalid worker difficulty")
        if type(template.height) is not int or template.height<1 or len(template.seed_hash)!=32:
            raise VerificationError("invalid template height or seed")
        blob=template.blockhashing_blob
        cursor=0
        for _ in range(3):cursor=_varint(blob,cursor)
        offset=cursor+32
        if offset+4>len(blob) or blob[:offset+4]!=template.blocktemplate_blob[:offset+4]:
            raise VerificationError("invalid native header alignment")
        identity=sha256(b"frg-bound-work-v1"+template.seed_hash+template.height.to_bytes(8,"big")+blob+worker_difficulty.to_bytes(16,"big")).hexdigest()[:32]
        work=BoundWork(template.height,blob,offset,template.seed_hash,worker_difficulty)
        with self._lock:
            self._preflight.register(identity,template.height)
            self._jobs[identity]=work
        return identity

    def inspect(self, job_id: str, nonce_hex: str, current_height: int,
                verifier: Callable[[bytes,bytes],bytes] | None) -> VerificationResult:
        if verifier is None or not callable(verifier):
            raise VerificationError("trusted RandomX verifier required")
        with self._lock:
            work=self._jobs.get(job_id) if isinstance(job_id,str) else None
        if work is None:raise VerificationError("unknown job")
        self._preflight.inspect(job_id,nonce_hex,current_height)
        patched=work.blob[:work.nonce_offset]+bytes.fromhex(nonce_hex)+work.blob[work.nonce_offset+4:]
        try:digest=verifier(work.seed,patched)
        except Exception as exc:raise VerificationError("trusted verifier failure") from exc
        if not isinstance(digest,bytes) or len(digest)!=32:
            raise VerificationError("invalid native digest")
        if int.from_bytes(digest,"little")>MAX_HASH//work.worker_difficulty:
            return VerificationResult("LOW_DIFFICULTY")
        return VerificationResult("POW_THRESHOLD_MET_UNCREDITED",digest.hex())
